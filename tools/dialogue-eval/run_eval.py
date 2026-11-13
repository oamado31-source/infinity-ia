# SPDX-License-Identifier: Apache-2.0
"""Run the fixed dialogue cases against the local model (Ollama) before a PR.

Each case runs --runs times (default 3) with the same model settings as the lab service and
passes with at least two thirds of the runs. Prints a table and writes a JSON report with the
answers to ~/.infinity-ai/dialogue-eval/ (outside the repository). Exit code 1 if a case fails.
Never stops or restarts Ollama.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import Catalog  # noqa: E402
from infinity_ai.dialogue.evaluation import DEFAULT_CASES, load_cases, run_case  # noqa: E402
from infinity_ai.dialogue.llm import OllamaProvider  # noqa: E402

REPORT_DIR = Path.home() / '.infinity-ai' / 'dialogue-eval'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--model', default='qwen3:8b')
    ap.add_argument('--ollama-url', default='http://127.0.0.1:11434')
    ap.add_argument('--runs', type=int, default=3)
    ap.add_argument('--case', action='append', default=[], help='run only these case ids')
    ap.add_argument('--cases', type=Path, default=DEFAULT_CASES)
    args = ap.parse_args()
    pack = load_partition(1369)
    cases = [c for c in load_cases(pack, args.cases) if not args.case or c.id in args.case]
    if not cases:
        print('nenhum caso selecionado')
        return 2
    provider = OllamaProvider(args.model, base_url=args.ollama_url)
    catalog = Catalog.load()
    results, failed = [], 0
    print(f'modelo {args.model}, {len(cases)} casos x {args.runs} rodadas')
    for case in cases:
        result = run_case(case, pack, provider, args.runs, catalog)
        results.append(result)
        failed += not result.passed
        reasons = Counter(f.split(':', 1)[1] for r in result.runs for f in r.flags
                          if f.startswith('attempt'))
        mark = 'OK ' if result.passed else 'FALHOU'
        print(f'{mark} {case.id:38} {result.passes}/{len(result.runs)} '
              f'reserva={result.fallbacks} recusas={dict(reasons) or "-"}')
        if not result.passed:
            for r in result.runs:
                if not r.passed:
                    print(f'      - {"; ".join(r.failures)} | {r.speech!r}')
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report = REPORT_DIR / f'{stamp}.json'
    report.write_text(json.dumps({
        'model': args.model, 'runs': args.runs, 'pack_revision': pack.revision,
        'cases': [{'id': r.case.id, 'passed': r.passed, 'passes': r.passes,
                   'required': r.required,
                   'runs': [{'passed': x.passed, 'status': x.status, 'speech': x.speech,
                             'flags': list(x.flags), 'failures': list(x.failures)}
                            for x in r.runs]} for r in results]},
        ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(cases) - failed}/{len(cases)} casos passaram; relatório em {report}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
