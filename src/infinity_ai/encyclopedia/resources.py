# SPDX-License-Identifier: Apache-2.0
"""SPEC-012 / CR-2026-032: the local inventory of resources converted from other games.

One entry per creature brought into BG2:EE from another game: its two sheets (source and
converted), the animation and the files it needs (INI, BAM), sounds and scripts, the community
project the files came from, the rights and the validation state. The entries live only in
`~/.infinity-ai/resources/install-<build>/resources.json` (the files and numbers are game data,
CR-2026-030); the repository keeps the schema and this validator.

Validation states, in order: DECLARED, ASSETS_PRESENT (every file in the build or the lab override),
DRAWN_IN_GAME (checked in the game by the maintainer), APPROVED (cleared for a quest).
"""
from __future__ import annotations

import json
from pathlib import Path

from .catalog import DEFAULT_BASE

RESOURCE_SCHEMA = 'infinity-ai.converted-resource.v1'
DEFAULT_DIR = Path.home() / '.infinity-ai' / 'resources'
STATES = ('DECLARED', 'ASSETS_PRESENT', 'DRAWN_IN_GAME', 'APPROVED')
OPEN_LICENSES = frozenset({'CC-BY-SA-4.0', 'CC-BY-4.0', 'MIT', 'APACHE-2.0', 'GPL-3.0'})


def inventory_path(build_fingerprint: str, base: Path = DEFAULT_DIR) -> Path:
    digest = build_fingerprint.split(':', 1)[-1][:16].lower()
    return Path(base) / f'install-{digest}' / 'resources.json'


def load_inventory(build_fingerprint: str, base: Path = DEFAULT_DIR) -> list[dict]:
    path = inventory_path(build_fingerprint, base)
    try:
        doc = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    if doc.get('build_fingerprint') != build_fingerprint:
        return []
    return list(doc.get('resources') or [])


def save_entry(build_fingerprint: str, entry: dict, base: Path = DEFAULT_DIR) -> Path:
    """Add or replace one entry (by resource_id) in the local inventory of this build."""
    path = inventory_path(build_fingerprint, base)
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = [e for e in load_inventory(build_fingerprint, base)
               if e.get('resource_id') != entry.get('resource_id')]
    entries.append(entry)
    path.write_text(json.dumps({'schema': 'infinity-ai.converted-resources.v1',
                                'build_fingerprint': build_fingerprint,
                                'resources': sorted(entries, key=lambda e: e['resource_id'])},
                               ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


def load_schema(base: Path = DEFAULT_BASE) -> dict:
    return json.loads((Path(base) / 'schemas' / 'converted-resource.v1.schema.json')
                      .read_text(encoding='utf-8'))


def load_sources(base: Path = DEFAULT_BASE) -> dict[str, dict]:
    doc = json.loads((Path(base) / 'sources.json').read_text(encoding='utf-8'))
    return {s['source_id']: s for s in doc['sources']}


def problems(entries: list[dict], *, sources: dict[str, dict], schema: dict | None = None,
             schema_check=None) -> list[str]:
    """Every problem of the inventory. `schema_check(doc, schema) -> list[str]` validates one
    entry (the tests pass a jsonschema validator)."""
    out: list[str] = []
    seen_ids: set[str] = set()
    seen_cres: set[str] = set()
    for entry in entries:
        rid = entry.get('resource_id', '?')
        if schema_check is not None and schema is not None:
            out += [f'{rid}: {msg}' for msg in schema_check(entry, schema)]
        for key, seen in (('resource_id', seen_ids), ('converted_cre_id', seen_cres)):
            value = entry.get(key)
            if value in seen:
                out.append(f'{rid}: {key} repetido ({value})')
            seen.add(value)
        source = sources.get(entry.get('conversion_source'))
        if source is None:
            out.append(f'{rid}: fonte desconhecida {entry.get("conversion_source")!r}')
        rights = entry.get('rights_status') or {}
        license_ = (source or {}).get('license') or rights.get('license') or 'NONE'
        if rights.get('use') == 'OPEN' and license_.upper() not in OPEN_LICENSES:
            out.append(f'{rid}: uso OPEN com licença {license_!r}: só LAB_ONLY')
        if rights.get('use') == 'LAB_ONLY' and license_.upper() not in OPEN_LICENSES \
                and not rights.get('approved_by'):
            out.append(f'{rid}: projeto sem licença aberta pede o aceite do mantenedor')
        state = entry.get('validation_status')
        if state in STATES and STATES.index(state) >= STATES.index('ASSETS_PRESENT'):
            missing = [a.get('resref') for k in ('animation_assets', 'sound_refs', 'script_refs')
                       for a in entry.get(k) or [] if not a.get('present')]
            if missing:
                out.append(f'{rid}: {state} com arquivos ausentes {missing}')
        if state in ('DRAWN_IN_GAME', 'APPROVED') and not entry.get('evidence_ref'):
            out.append(f'{rid}: {state} sem evidência')
    return out
