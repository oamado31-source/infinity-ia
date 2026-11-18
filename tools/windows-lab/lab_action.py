# SPDX-License-Identifier: Apache-2.0
"""ADR-0136 (gate P3) lab command: create or remove one creature of ours in the running game.

Only the maintainer dispatches in this gate (D2). The command validates the request through the
gateway, records it on the campaign's current branch, writes override/INFAIACT.lua, waits for the
EEex module's answer in the loader log (INFAI-ACT) and records the result. The request file goes
back to empty at the end. Use a disposable save (INFINITY-P3-DESCARTAVEL). Only our creature files
(build_templates.py, deployed with the game closed) can be created.

  export INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
  python tools/windows-lab/lab_action.py spawn --cre IA<...> --area AR0406 [--x N --y N --facing N]
  python tools/windows-lab/lab_action.py despawn --name INFAI_<id> --area AR0406
  python tools/windows-lab/lab_action.py owned
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import json  # noqa: E402

from infinity_ai.actions.gateway import (  # noqa: E402
    ACT_RESREF, ActionError, PLACEHOLDER_ACT, despawn_request, load_templates, owned_creatures,
    parse_receipts, record_requested, record_result, render_request, spawn_request,
)
from infinity_ai.bridge.manifest import build_fingerprint  # noqa: E402
from infinity_ai.state.store import CampaignStore  # noqa: E402
from lab_ssh import SshByteSource, grep_log, put_override_file, run_ps, ssh_from_env  # noqa: E402


def deployed_templates(ssh, game_root: str, fingerprint: str) -> dict[str, str]:
    """Our creature files of this build that are really in the VM's override."""
    there = {n.rsplit('.', 1)[0].upper()
             for n in SshByteSource(ssh, game_root).list_dir('override', '.cre')}
    return {r: n for r, n in load_templates(fingerprint).items() if r in there}


def current_game_time(ssh, game_root: str) -> int | None:
    """The game time of the probe's latest line (INFAI-P2, every few seconds while playing)."""
    out = run_ps(ssh, f"""
$f = Join-Path '{game_root}' 'InfinityLoader.log'
if (Test-Path -LiteralPath $f) {{ (Select-String -LiteralPath $f -Pattern 'INFAI-P2 ' | Select-Object -Last 1).Line }}
""", timeout=60).strip()
    index = out.find('INFAI-P2 ')
    if index < 0:
        return None
    try:
        value = json.loads(out[index + len('INFAI-P2 '):])['fields'].get('host.game_time')
    except (ValueError, KeyError, TypeError):
        return None
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def wait_receipt(ssh, game_root: str, action_id: str, timeout: float):
    """The module's last answer for this action: DONE or REFUSED, or the ACCEPTED it reached."""
    deadline, last = time.monotonic() + timeout, None
    while time.monotonic() < deadline:
        lines = grep_log(ssh, game_root, f'INFAI-ACT .*{action_id}', limit=10)
        receipts = [r for r in parse_receipts('\n'.join(lines)) if r.action_id == action_id]
        if receipts:
            last = receipts[-1]
            if last.status in ('DONE', 'REFUSED'):
                return last
        time.sleep(1.0)
    return last


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('op', choices=('spawn', 'despawn', 'owned'))
    ap.add_argument('--cre')
    ap.add_argument('--name')
    ap.add_argument('--area')
    ap.add_argument('--x', type=int, default=-1)
    ap.add_argument('--y', type=int, default=-1)
    ap.add_argument('--facing', type=int, default=0)
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--campaign', default='lab-s1f')
    ap.add_argument('--db', type=Path,
                    default=Path.home() / '.infinity-ai' / 'campaigns' / 'lab-s1f.sqlite3')
    ap.add_argument('--timeout', type=float, default=30.0)
    ap.add_argument('--pinned-manifest', type=Path, default=Path.home() / 'Developer' /
                    'infinity-ia-lab' / 'evidence' / 's1x-manifest-2026-11-18b-pinned.json')
    args = ap.parse_args()
    store = CampaignStore.open(args.db, args.campaign)
    branch = store.active_branch()
    owned = owned_creatures(store, branch)
    if args.op == 'owned':
        print(f'ramo {branch}: {owned or "nenhuma criatura nossa"}')
        return 0
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    try:
        if args.op == 'spawn':
            fingerprint = build_fingerprint(json.loads(
                args.pinned_manifest.read_text(encoding='utf-8-sig')))
            req = spawn_request(args.cre or '', args.area or '', x=args.x, y=args.y,
                                facing=args.facing,
                                templates=deployed_templates(ssh, args.game_root, fingerprint))
        else:
            req = despawn_request(args.name or '', args.area or '', owned=set(owned))
    except ActionError as exc:
        print(f'recusado pelo gateway: {exc.code}')
        return 2
    game_time = current_game_time(ssh, args.game_root)
    try:
        record_requested(store, branch, req, game_time=game_time)
    except ActionError as exc:
        print(f'recusado pelo gateway: {exc.code} (o jogo esta aberto, com uma partida carregada?)')
        return 2
    put_override_file(ssh, args.game_root, f'{ACT_RESREF}.lua', render_request(req).encode('utf-8'))
    print(f'pedido {req.action_id}: {req.op} {req.cre or req.name} em {req.area} '
          f'(ramo {branch}, t={game_time})')
    try:
        receipt = wait_receipt(ssh, args.game_root, req.action_id, args.timeout)
    finally:
        put_override_file(ssh, args.game_root, f'{ACT_RESREF}.lua', PLACEHOLDER_ACT.encode('utf-8'))
    state = record_result(store, branch, req, receipt,
                          game_time=current_game_time(ssh, args.game_root) or game_time)
    print(f'resposta do jogo: {receipt}' if receipt else 'sem resposta do jogo')
    print(f'estado: {state}' + (f'  nome da criatura: {req.name}' if req.op == 'SPAWN_CREATURE'
                                and state == 'HOST_CONFIRMED' else ''))
    return 0 if state == 'HOST_CONFIRMED' else 1


if __name__ == '__main__':
    sys.exit(main())
