# SPDX-License-Identifier: Apache-2.0
"""Run the fixed dialogue cases against the local model (Ollama) or Claude (ADR-0147).

Each case runs --runs times (default 3) with the same model settings as the lab service and
passes with at least two thirds of the runs. Prints a table with the time of each answer
(retries included; one warm-up request loads the model first and is not counted) and writes a
JSON report with the answers to ~/.infinity-ai/dialogue-eval/ (outside the repository). Exit
code 1 if a case fails. Never stops or restarts Ollama.

  --provider claude   Claude Haiku 5.5 by default (opt-in, ADR-0147); the key comes from the
                      host's ANTHROPIC_API_KEY. The report adds the tokens and the estimated cost.
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
from infinity_ai.dialogue.layers import LayerPolicy  # noqa: E402
from infinity_ai.dialogue.llm import (CLAUDE_MODEL, AnthropicProvider, LlmError,  # noqa: E402
                                      OllamaProvider, claude_cost)

REPORT_DIR = Path.home() / '.infinity-ai' / 'dialogue-eval'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--provider', choices=('ollama', 'claude'), default='ollama')
    ap.add_argument('--camadas', action='store_true',
                    help='ADR-0147: the lab service layers (code, then Ollama; with --provider '
                         'claude, Claude as the last layer over Ollama)')
    ap.add_argument('--model', default=None,
                    help=f'default qwen3:30b-a3b (ollama) or {CLAUDE_MODEL} (claude)')
    ap.add_argument('--ollama-url', default='http://127.0.0.1:11434')
    ap.add_argument('--runs', type=int, default=3)
    ap.add_argument('--case', action='append', default=[], help='run only these case ids')
    ap.add_argument('--cases', type=Path, default=DEFAULT_CASES)
    ap.add_argument('--timeout', type=float, default=30.0,
                    help='seconds per model request (the lab service uses 30)')
    args = ap.parse_args()
    pack = load_partition(1369)
    cases = [c for c in load_cases(pack, args.cases) if not args.case or c.id in args.case]
    if not cases:
        print('nenhum caso selecionado')
        return 2
    layers = None
    if args.provider == 'claude' and not args.camadas:
        args.model = args.model or CLAUDE_MODEL
        provider = AnthropicProvider(args.model, timeout_s=args.timeout)
    else:
        args.model = args.model or 'qwen3:30b-a3b'
        provider = OllamaProvider(args.model, base_url=args.ollama_url, timeout_s=args.timeout)
        warm = OllamaProvider(args.model, base_url=args.ollama_url, timeout_s=300)
        try:
            warm.generate([{'role': 'user', 'content': 'ok'}])  # load the model; not counted
        except LlmError as exc:
            print(f'aquecimento falhou: {exc}')
        if args.camadas:
            claude = AnthropicProvider(CLAUDE_MODEL, timeout_s=args.timeout) \
                if args.provider == 'claude' else None
            layers = LayerPolicy(claude=claude)
    catalog = Catalog.load()
    results, failed = [], 0
    print(f'modelo {args.model}{" com camadas" if layers else ""}'
          f'{" e Claude" if layers and layers.claude else ""}, '
          f'{len(cases)} casos x {args.runs} rodadas')
    for case in cases:
        result = run_case(case, pack, provider, args.runs, catalog, layers)
        results.append(result)
        failed += not result.passed
        reasons = Counter(f.split(':', 1)[1] for r in result.runs for f in r.flags
                          if f.startswith('attempt'))
        mark = 'OK ' if result.passed else 'FALHOU'
        print(f'{mark} {case.id:38} {result.passes}/{len(result.runs)} '
              f'tempo={result.mean_seconds:.1f}s(máx {result.max_seconds:.1f}s) '
              f'reserva={result.fallbacks} recusas={dict(reasons) or "-"}')
        if not result.passed:
            for r in result.runs:
                if not r.passed:
                    print(f'      - {"; ".join(r.failures)} | {r.speech!r}')
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report = REPORT_DIR / f'{stamp}.json'
    billed = layers.claude if layers is not None and layers.claude is not None else provider
    usage = getattr(billed, 'usage_total', None)
    cost = claude_cost(billed.model, usage) if usage else None
    report.write_text(json.dumps({
        'provider': args.provider, 'model': args.model, 'runs': args.runs,
        'layers': bool(args.camadas),
        'pack_revision': pack.revision, 'timeout_s': args.timeout,
        'usage': usage, 'requests': getattr(provider, 'requests', None),
        'cost_usd': None if cost is None else round(cost, 4),
        'cases': [{'id': r.case.id, 'passed': r.passed, 'passes': r.passes,
                   'required': r.required,
                   'question': r.case.question, 'speaker': r.case.speaker,
                   'history': [list(h) for h in r.case.history],
                   'mean_seconds': round(r.mean_seconds, 2),
                   'runs': [{'passed': x.passed, 'status': x.status, 'seconds': x.seconds,
                             'model': x.model,
                             'speech': x.speech,
                             'flags': list(x.flags), 'failures': list(x.failures)}
                            for x in r.runs]} for r in results]},
        ensure_ascii=False, indent=1), encoding='utf-8')
    times = sorted(x.seconds for r in results for x in r.runs)
    p90 = times[min(len(times) - 1, int(len(times) * 0.9))]
    print(f'{len(cases) - failed}/{len(cases)} casos passaram; tempo médio '
          f'{sum(times) / len(times):.1f}s, p90 {p90:.1f}s; relatório em {report}')
    if layers is not None:
        print('quem respondeu: ' + ', '.join(
            f'{m or "?"} {n}' for m, n in Counter(x.model for r in results for x in r.runs)
            .most_common()))
    if usage:
        print(f'tokens: {usage} em {billed.requests} pedidos; custo estimado '
              f'{"?" if cost is None else f"US$ {cost:.4f}"}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
