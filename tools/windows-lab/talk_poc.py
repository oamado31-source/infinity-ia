# SPDX-License-Identifier: Apache-2.0
"""Stage 0 of the INQUIRY channel: proves the in-game dialogue box round trip, with no LLM.

Reads `INFAI-TALK` lines from the loader log over SSH and answers each one with an echo through
`override/INFAIRSP.lua`. It prints metadata only (no player text): request id, speaker, listeners
and the time between the request being written and the reply file being in place. Lab only
(CR-2026-001); the reply file is removed on exit.

  export INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
  python tools/windows-lab/talk_poc.py --deploy     # copy M_INFAIT.lua + INFAITLK.menu (restart the game after)
  python tools/windows-lab/talk_poc.py              # answer requests until Ctrl+C
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.bridge.talk import (  # noqa: E402
    PLACEHOLDER_REPLY, REPLY_RESREF, parse_talk_requests, render_reply,
)
from lab_ssh import (  # noqa: E402
    SshLogSource, now_iso, put_override_file, ssh_from_env,
)

PROBE_DIR = ROOT / 'tools' / 'eeex-probe'
FILES = ('M_INFAIT.lua', 'INFAITLK.menu')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--deploy', action='store_true', help='copy the dialogue box files and exit')
    ap.add_argument('--interval', type=float, default=1.0)
    args = ap.parse_args()
    ssh = ssh_from_env('INFINITY_LAB_SSH')

    if args.deploy:
        for name in FILES:
            put_override_file(ssh, args.game_root, name, (PROBE_DIR / name).read_bytes())
            print(f'copiado: override\\{name}')
        put_override_file(ssh, args.game_root, f'{REPLY_RESREF}.lua', PLACEHOLDER_REPLY.encode())
        print(f'copiado: override\\{REPLY_RESREF}.lua (resposta vazia; precisa existir ao abrir o jogo)')
        print('reabra o jogo para carregar o modulo')
        return 0

    source = SshLogSource(ssh, args.game_root)
    seen: set[str] = set(r.req_id for r in parse_talk_requests(source.fetch()[0]))
    print(f'{now_iso()} aguardando pedidos (ignorando {len(seen)} antigos)')
    try:
        while True:
            text, _ = source.fetch()
            for req in parse_talk_requests(text):
                if req.req_id in seen:
                    continue
                seen.add(req.req_id)
                started = time.monotonic()
                listeners = ', '.join(n.split(':', 1)[1] for n in req.listeners or ()) or 'ninguem'
                speech = (f'(eco) Recebi {len(req.text)} caracteres. Ouvindo: {listeners}.'
                          if not req.speaker_dead else '(eco) ...')
                put_override_file(ssh, args.game_root, f'{REPLY_RESREF}.lua',
                         render_reply(req.req_id, speech).encode('utf-8'))
                leader = req.selected_leader
                leader_label = "-"
                if leader is not None:
                    leader_chr = leader.charisma_active if leader.charisma_active is not None else "-"
                    leader_label = (f'{leader.script_name or leader.display_name}@p{leader.portrait_index}'
                                    f':chr={leader_chr}')
                chr_active = req.speaker_charisma_active if req.speaker_charisma_active is not None else "-"
                morale = (req.speaker_engine_morale_current
                          if req.speaker_engine_morale_current is not None else "-")
                morale_break = (req.speaker_engine_morale_break_active
                                if req.speaker_engine_morale_break_active is not None else "-")
                print(f'{now_iso()} pedido={req.req_id} falante={req.speaker_script or "-"} '
                      f'morto={req.speaker_dead} area={req.area} t={req.game_time} '
                      f'chr_ativo={chr_active} morale_engine_atual={morale} '
                      f'morale_break_engine_ativo={morale_break} selected_leader={leader_label} '
                      f'ouvintes={list(req.listeners) if req.listeners is not None else None} '
                      f'resposta_gravada_em={int((time.monotonic() - started) * 1000)}ms')
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        put_override_file(ssh, args.game_root, f'{REPLY_RESREF}.lua', PLACEHOLDER_REPLY.encode())
        print(f'{now_iso()} resposta removida; fim')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
