# SPDX-License-Identifier: Apache-2.0
"""SPEC-005 lab helper: build the local area inventory from the VM's game copy (read-only).

Reads KEY/BIF/WMP/TLK slices over SSH into memory and writes only the derived inventory to
~/.infinity-ai/knowledge/ (outside the repository, REQ-CANON-004).

  export INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
  python tools/windows-lab/build_area_inventory.py --language pt_BR
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.bridge.manifest import build_fingerprint  # noqa: E402
from infinity_ai.gamedata.inventory import build_inventory, write_inventory  # noqa: E402
from lab_ssh import SshByteSource, live_manifest, ssh_from_env  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--language', default='pt_BR')
    args = ap.parse_args()
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    fingerprint = build_fingerprint(live_manifest(ssh, args.game_root, 'inventory-manifest.json'))
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
