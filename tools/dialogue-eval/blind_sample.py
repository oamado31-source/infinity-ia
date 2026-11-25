#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""ADR-0147, phase 1: a blind sample of two battery reports for the maintainer to grade.

  python tools/dialogue-eval/blind_sample.py REPORT_A.json REPORT_B.json [--count 15] [--seed 1]
  python tools/dialogue-eval/blind_sample.py --reveal KEY.json

Picks --count cases present in both reports and, for each, the first answer of each model, in a
random order per case (answer 1 and answer 2). Writes the sheet to ~/Downloads and the key (which
answer is which model) to ~/.infinity-ai/dialogue-eval/, both outside the repository; --reveal
prints the key after the grades are in.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

REPORT_DIR = Path.home() / '.infinity-ai' / 'dialogue-eval'
SHEET_DIR = Path.home() / 'Downloads'


def first_answer(case: dict) -> str:
    runs = case.get('runs') or []
    return runs[0]['speech'] if runs else ''


def build(a: dict, b: dict, count: int, seed: int) -> tuple[str, dict]:
    by_id = {c['id']: c for c in b['cases']}
    common = [c for c in a['cases'] if c['id'] in by_id]
    rng = random.Random(seed)
    picked = rng.sample(common, min(count, len(common)))
    lines = ['# Amostra cega: qualidade das falas', '',
             'Para cada pergunta, dê uma nota de 1 a 5 a cada resposta (naturalidade em português, '
             'personagem, conteúdo) e, se quiser, diga qual prefere. Os modelos só são revelados '
             'depois das notas.', '']
    key = {'a': a['model'], 'b': b['model'], 'seed': seed, 'cases': []}
    for n, case in enumerate(picked, 1):
        answers = [('a', first_answer(case)), ('b', first_answer(by_id[case['id']]))]
        rng.shuffle(answers)
        key['cases'].append({'n': n, 'id': case['id'], 'order': [m for m, _ in answers]})
        sp = case.get('speaker') or {}
        who = ', '.join(str(x) for x in (sp.get('name') or sp.get('npc_id', '?'),
                                         sp.get('occupation')) if x)
        mind = f" (SAB {sp['wis']}, INT {sp['int']})" if 'wis' in sp and 'int' in sp else ''
        lines += [f'## {n}. {who}{mind}', '']
        for asked, said in case.get('history') or []:
            lines += [f'- *antes, jogador:* {asked}', f'- *antes, NPC:* {said}']
        lines += [f'**Jogador:** {case.get("question", "?")}', '']
        for i, (_, speech) in enumerate(answers, 1):
            lines += [f'**Resposta {i}:** {speech or "(sem resposta)"}', '']
        lines += ['Nota resposta 1: __  Nota resposta 2: __  Preferida: __', '']
    return '\n'.join(lines), key


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('reports', nargs='*', type=Path)
    ap.add_argument('--count', type=int, default=15)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--reveal', type=Path)
    args = ap.parse_args()
    if args.reveal:
        key = json.loads(args.reveal.read_text(encoding='utf-8'))
        for c in key['cases']:
            print(f"{c['n']:2}. {c['id']:38} 1={key[c['order'][0]]}  2={key[c['order'][1]]}")
        return 0
    if len(args.reports) != 2:
        ap.error('two reports, or --reveal KEY')
    a, b = (json.loads(p.read_text(encoding='utf-8')) for p in args.reports)
    sheet, key = build(a, b, args.count, args.seed)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    sheet_path = SHEET_DIR / f'INFINITY_AI_amostra_cega_{stamp}.md'
    key_path = REPORT_DIR / f'blind-key-{stamp}.json'
    sheet_path.write_text(sheet, encoding='utf-8')
    key_path.write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'folha: {sheet_path}\nchave: {key_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
