# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 lab helper: build the local area inventory from the VM's game copy (read-only).

Reads KEY/BIF/WMP/TLK slices over SSH into memory and writes only the derived inventory to
~/.infinity-ai/knowledge/ (outside the repository, REQ-CANON-004). `--residents` also lists the
creatures the game places in the areas of the pinned canon pack (ADR-0116 established residents).

  export INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
  python tools/windows-lab/build_area_inventory.py --language pt_BR [--residents]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.bridge.manifest import build_fingerprint  # noqa: E402
from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.gamedata.inventory import (  # noqa: E402
    build_inventory, build_residents, write_inventory,
)
from lab_ssh import SshByteSource, live_manifest, ssh_from_env  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--language', default='pt_BR')
    ap.add_argument('--residents', action='store_true',
                    help='also list creatures placed in the canon pack areas')
    ap.add_argument('--year', type=int, default=1369, help='canon pack partition (DR year)')
    args = ap.parse_args()
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    fingerprint = build_fingerprint(live_manifest(ssh, args.game_root, 'inventory-manifest.json'))
    if args.residents:
        areas = {a for e in load_partition(args.year).entries.values() for a in e.area_resrefs}
        residents = build_residents(SshByteSource(ssh, args.game_root), language=args.language,
                                    build_fingerprint=fingerprint, areas=areas)
        path = write_inventory(residents)
        print(f'habitantes={len(residents.residents)} areas={len(residents.areas)} '
              f'sem_script={residents.skipped_without_script}')
        print(f'gravado em {path}')
    inventory = build_inventory(SshByteSource(ssh, args.game_root), language=args.language,
                                build_fingerprint=fingerprint)
    path = write_inventory(inventory)
    named = sum(1 for a in inventory.areas if a.display_name)
    print(f'build {fingerprint[:19]}… areas={len(inventory.areas)} '
          f'no_mapa={sum(a.on_worldmap for a in inventory.areas)} com_nome={named}')
    print(f'gravado em {path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
