# SPDX-License-Identifier: Apache-2.0
"""Pin the current canon pack revision on the campaign's active branch (ADR-0058, explicit only).

Anchors the pin at the game's current time (read from the probe over SSH when INFINITY_LAB_SSH
is set and the log is fresh; otherwise the latest recorded event), so ADR-0114 residence time for
this revision counts from here on. Re-running with the same revision is a no-op.

  python tools/windows-lab/pin_canon_pack.py [--campaign lab-s1] [--year 1369]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.bridge.eeex_log import GAME_TIME_FIELD, parse_latest_snapshot  # noqa: E402

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.canon.pin import check_pin, pin_pack  # noqa: E402
from infinity_ai.state.store import CampaignStore  # noqa: E402


def probe_game_time(game_root: str) -> int | None:
    if not os.environ.get('INFINITY_LAB_SSH'):
        return None
    from lab_ssh import SshLogSource, ssh_from_env
    text, age = SshLogSource(ssh_from_env('INFINITY_LAB_SSH'), game_root).fetch()
    snap = parse_latest_snapshot(text) if age <= 10 else None
    value = snap.fields.get(GAME_TIME_FIELD) if snap else None
    return int(value) if value is not None else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--campaign', default='lab-s1')
    ap.add_argument('--db', type=Path,
                    default=Path.home() / '.infinity-ai' / 'campaigns' / 'lab-s1.sqlite3')
    ap.add_argument('--year', type=int, default=1369)
    ap.add_argument('--evidence', default='LAB_OBSERVED')
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    args = ap.parse_args()
    pack = load_partition(args.year)
    with CampaignStore.open(args.db, args.campaign) as store:
        branch = store.active_branch()
        before = check_pin(store, branch, pack)
        live = probe_game_time(args.game_root)
        anchor = live if live is not None else store.latest_game_time(branch)
        print(f'tempo de jogo para o pin: {anchor} ({"sonda" if live is not None else "ultimo evento"})')
        event, new = pin_pack(store, branch, pack, evidence=args.evidence, game_time=anchor)
        print(f'ramo {branch}: {before.value} -> {check_pin(store, branch, pack).value} '
              f'(revisao {pack.revision[:19]}..., {len(pack.entries)} entradas, '
              f't={event.game_time}, {"novo pin" if new else "ja pinado"})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
