# SPDX-License-Identifier: Apache-2.0
"""SPEC-012 lab helper (CR-2026-030): census of the characters the game places in its areas.

Reads every area of the VM's game copy over SSH into memory (read-only) and writes only the derived
catalog to ~/.infinity-ai/encyclopedia/install-<build>/census.<language>.json, outside the
repository. It also writes a Markdown report for the maintainer (by default in ~/Downloads): how
many characters, where, which already have a curated record, and a suggested curation queue.

  export INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
  python tools/windows-lab/build_encyclopedia.py --characters [--language pt_BR] [--report <path>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.bridge.manifest import build_fingerprint  # noqa: E402
from infinity_ai.gamedata.census import build_census, census_report, write_census  # noqa: E402
from infinity_ai.gamedata.inventory import load_local_names  # noqa: E402
from lab_ssh import SshByteSource, live_manifest, ssh_from_env  # noqa: E402


def curated_ids() -> set[str]:
    """The NPC ids that already have a curated record (via their curation file)."""
    out = set()
    for path in (ROOT / 'knowledge' / 'encyclopedia' / 'characters').rglob('*.json'):
        curation = (json.loads(path.read_text(encoding='utf-8')).get('refs') or {}).get('curation')
        if curation and (ROOT / curation).is_file():
            out.add(json.loads((ROOT / curation).read_text(encoding='utf-8'))['npc_id'])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--language', default='pt_BR')
    ap.add_argument('--characters', action='store_true', help='census of every area (SPEC-012)')
    ap.add_argument('--report', type=Path,
                    default=Path.home() / 'Downloads' / 'INFINITY_AI_Censo_Personagens_BG2.md')
    args = ap.parse_args()
    if not args.characters:
        ap.error('nothing to do: pass --characters')
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    fingerprint = build_fingerprint(live_manifest(ssh, args.game_root, 'encyclopedia-manifest.json'))
    census = build_census(SshByteSource(ssh, args.game_root), language=args.language,
                          build_fingerprint=fingerprint)
    path = write_census(census)
    report = census_report(census, curated=curated_ids(),
                           area_names=load_local_names(fingerprint, args.language))
    args.report.write_text(report, encoding='utf-8')
    chars = census.characters()
    print(f'areas={len(census.areas)} entradas={len(census.entries)} personagens={len(chars)} '
          f'com_dialogo={sum(1 for c in chars if c.dialog)}')
    print(f'catalogo local: {path}')
    print(f'relatorio: {args.report}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
