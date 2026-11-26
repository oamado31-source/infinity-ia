#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""SPEC-013: check quest files and list every problem by name (errors block, warnings inform).

  python tools/quest-author/check_quest.py knowledge/quests/sarevok-diary.pt_BR.json
  python tools/quest-author/check_quest.py ~/.infinity-ai/quests/local/*.json
  python tools/quest-author/check_quest.py --no-local FILE   # format only, no local inventory

Besides the format, it checks the quest against what exists: checked curations (knowledge/npcs),
the build's areas and our installed creature templates (local inventories in ~/.infinity-ai,
never the repository) and the names the world knows (canon pack, residents, curations). Exit
code 1 when any file has an error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.personality.identity import load_curations  # noqa: E402
from infinity_ai.quests.authoring import AuthoringContext, check_quest  # noqa: E402

LOCAL = Path.home() / '.infinity-ai'
_NAME = re.compile(r"[A-ZÀ-Ý][\wÀ-ÿ'-]{2,}")


def _single(pattern: str) -> Path | None:
    found = sorted(LOCAL.glob(pattern))
    return found[-1] if found else None


def _read(path: Path | None) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8')) if path else {}
    except (OSError, ValueError):
        return {}


def local_context(year: int, language: str) -> AuthoringContext:
    pack = load_partition(year)
    curations = load_curations(pack)
    areas_doc = _read(_single(f'knowledge/install-*/areas.{language}.json'))
    residents_doc = _read(_single(f'knowledge/install-*/residents.{language}.json'))
    templates_doc = _read(_single('templates/install-*/templates.json'))
    names: set[str] = set()
    for entry in pack.entries.values():
        names |= set(_NAME.findall(f'{entry.title} {entry.summary}'))
    for r in residents_doc.get('residents', []):
        names |= set(_NAME.findall(r.get('display_name') or ''))
    for c in curations.values():
        names |= set(_NAME.findall(' '.join(c.self_facts)))
    return AuthoringContext(
        curated=frozenset(curations),
        areas=frozenset(a['resref'] for a in areas_doc.get('areas', [])) or None,
        templates=frozenset(t['resref'] for t in templates_doc.get('templates', [])) or None,
        names=frozenset(names))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('files', nargs='+', type=Path)
    ap.add_argument('--no-local', action='store_true', help='format only')
    ap.add_argument('--year', type=int, default=1369)
    ap.add_argument('--language', default='pt_BR')
    args = ap.parse_args()
    context = None if args.no_local else local_context(args.year, args.language)
    if context is not None:
        missing = [n for n, v in (('áreas da build', context.areas),
                                  ('modelos de criatura', context.templates)) if v is None]
        if missing:
            print('sem inventário local de ' + ' e '.join(missing) + ': essa conferência foi pulada')
    failed = 0
    for path in args.files:
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            print(f'\n{path}: não abre como JSON ({exc})')
            failed += 1
            continue
        report = check_quest(doc, context)
        mark = 'OK' if report.ok else 'RECUSADA'
        print(f'\n{path}: {mark} ({len(report.errors)} erros, {len(report.warnings)} avisos)')
        for issue in report.errors:
            print(f'  ERRO  {issue}')
        for issue in report.warnings:
            print(f'  aviso {issue}')
        failed += not report.ok
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
