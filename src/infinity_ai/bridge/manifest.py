# SPDX-License-Identifier: Apache-2.0
"""P0 build manifest: fingerprint, modpack hash and a pre-check of the collected inventory.

The manifest comes from `tools/windows-lab/p0-collect-manifest.ps1`, which only reads files.
Canonical hashing lives here (one implementation) so the collector stays dumb. A clean manifest
is a necessary condition for P0, not P0 itself: the base run and throwaway save are manual steps.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

MANIFEST_SCHEMA_VERSION = 'infinity-ai.p0.build-manifest.v1'
_KNOWN_MACHINES = {'x86', 'x64'}


class Severity(str, Enum):
    BLOCK = 'BLOCK'
    REVIEW = 'REVIEW'


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    detail: str


@dataclass(frozen=True)
class ManifestAssessment:
    status: str  # MANIFEST_OK | MANIFEST_BLOCKED
    build_fingerprint: str | None
    modpack_hash: str | None
    findings: tuple[Finding, ...]


def _digest(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    return 'sha256:' + hashlib.sha256(canonical.encode('ascii')).hexdigest()


def _files(entries: Any) -> list[list[str]]:
    if not isinstance(entries, list):
        raise ValueError('file list must be an array')
    out = []
    for e in entries:
        path, sha = e.get('path'), e.get('sha256')
        if not isinstance(path, str) or not path or not isinstance(sha, str) or len(sha) != 64:
            raise ValueError(f'invalid file entry: {e!r}')
        if path.startswith(('/', '\\')) or ':' in path or '..' in path.replace('\\', '/').split('/'):
            raise ValueError(f'file path must be relative to the install root: {path!r}')
        out.append([path.replace('\\', '/').lower(), sha.lower()])
    return sorted(out)


def build_fingerprint(manifest: dict[str, Any]) -> str:
    game = manifest['game']
    exe = game['executable']
    return _digest({
        'executable': {'sha256': exe['sha256'].lower(), 'file_version': exe['file_version'],
                       'pe_machine': exe['pe_machine']},
        'files': _files(game['files']),
    })


# Transient data files written while the game runs (ADR-0116 reply channel): not part of the mod.
TRANSIENT_OVERRIDE = frozenset({'override/infairsp.lua'})


def modpack_hash(manifest: dict[str, Any]) -> str:
    game = manifest['game']
    return _digest({
        'override': [f for f in _files(game['override_files']) if f[0] not in TRANSIENT_OVERRIDE],
        'weidu_log_sha256': game.get('weidu_log_sha256'),
        'eeex_markers': sorted(m.lower() for m in game['eeex_markers']),
        'mod_setup_markers': sorted(m.lower() for m in game['mod_setup_markers']),
    })


def assess_manifest(manifest: dict[str, Any]) -> ManifestAssessment:
    findings: list[Finding] = []
    if manifest.get('schema_version') != MANIFEST_SCHEMA_VERSION:
        findings.append(Finding('SCHEMA_VERSION', Severity.BLOCK,
                                f'expected {MANIFEST_SCHEMA_VERSION}'))
        return ManifestAssessment('MANIFEST_BLOCKED', None, None, tuple(findings))

    env = manifest.get('environment', {})
    if str(env.get('processor_architecture', '')).upper() == 'ARM64':
        findings.append(Finding('HOST_ARM64', Severity.REVIEW,
                                'Windows on ARM: the game runs under x86/x64 emulation; '
                                'ADR-0005 assumed native Windows (see CR-2026-001).'))
    if env.get('is_virtual_machine'):
        findings.append(Finding('VIRTUAL_MACHINE', Severity.REVIEW,
                                f'Guest of {env.get("vm_vendor") or "unknown hypervisor"}.'))

    game = manifest.get('game') or {}
    if not game.get('detected'):
        findings.append(Finding('GAME_NOT_FOUND', Severity.BLOCK,
                                'No BG2:EE install detected; pass -GameRoot to the collector.'))
        return ManifestAssessment('MANIFEST_BLOCKED', None, None, tuple(findings))

    try:
        fingerprint, modpack = build_fingerprint(manifest), modpack_hash(manifest)
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        findings.append(Finding('MALFORMED_MANIFEST', Severity.BLOCK, str(exc)))
        return ManifestAssessment('MANIFEST_BLOCKED', None, None, tuple(findings))

    machine = game['executable']['pe_machine']
    if machine not in _KNOWN_MACHINES:
        findings.append(Finding('UNEXPECTED_PE_MACHINE', Severity.REVIEW, str(machine)))
    if game.get('weidu_log_sha256'):
        findings.append(Finding('WEIDU_LOG_PRESENT', Severity.BLOCK,
                                'WeiDU.log found: install is modded, not vanilla.'))
    if game['eeex_markers']:
        findings.append(Finding('EEEX_PRESENT', Severity.BLOCK,
                                'EEex files found: P0 must run before P1 on a clean copy.'))
    if game['mod_setup_markers']:
        findings.append(Finding('MOD_SETUP_PRESENT', Severity.BLOCK,
                                'Mod installers found in the game root.'))
    if game['override_files']:
        findings.append(Finding('OVERRIDE_NOT_EMPTY', Severity.REVIEW,
                                f'{len(game["override_files"])} file(s) in override/.'))

    blocked = any(f.severity is Severity.BLOCK for f in findings)
    return ManifestAssessment('MANIFEST_BLOCKED' if blocked else 'MANIFEST_OK',
                              fingerprint, modpack, tuple(findings))
