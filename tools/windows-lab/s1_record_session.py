# SPDX-License-Identifier: Apache-2.0
"""S1 (single player) lab session: bridge -> recorder -> campaign SQLite, then backup and recall.

Lab-only helper (CR-2026-001, ADR-0113). Reads the game over SSH; writes only the local campaign
database and its backup on this machine, never anything in the game folder.

  export INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
  python tools/windows-lab/s1_record_session.py --pinned-manifest <manifest.json> --duration 900
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.bridge.domain import (  # noqa: E402
    Allowlist, Evidence, FieldPolicy, SessionIdentity, Visibility,
)
from infinity_ai.bridge.eeex_log import (  # noqa: E402
    ADAPTER_VERSION, AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD, EEexLogAdapter,
    parse_latest_snapshot,
)
from infinity_ai.bridge.manifest import build_fingerprint, modpack_hash  # noqa: E402
from infinity_ai.bridge.service import ReadOnlyBridge  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.state.backup import backup, verify_restore  # noqa: E402
from infinity_ai.state.recorder import ObservationRecorder, RecordAction  # noqa: E402
from infinity_ai.state.store import CampaignStore  # noqa: E402
from lab_ssh import SshLogSource, live_manifest, now_iso, ssh_from_env  # noqa: E402

FIELDS = (AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD)
DEFAULT_DB = Path.home() / '.infinity-ai' / 'campaigns'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--pinned-manifest', required=True, type=Path)
    ap.add_argument('--campaign', default='lab-s1')
    ap.add_argument('--db-dir', type=Path, default=DEFAULT_DB)
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--duration', type=float, default=600.0)
    ap.add_argument('--interval', type=float, default=4.0)
    args = ap.parse_args()

    pinned_manifest = json.loads(args.pinned_manifest.read_text(encoding='utf-8-sig'))
    pin_build, pin_modpack = build_fingerprint(pinned_manifest), modpack_hash(pinned_manifest)
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    live = live_manifest(ssh, args.game_root, out_name='s1-live-manifest.json')
    live_build, live_modpack = build_fingerprint(live), modpack_hash(live)
    print(f'live matches pinned: {(live_build, live_modpack) == (pin_build, pin_modpack)}')

    source = SshLogSource(ssh, args.game_root)
    adapter = EEexLogAdapter(source, campaign_id=args.campaign, branch_id='main',
                             build_fingerprint=live_build, modpack_hash=live_modpack)
    allowlist = Allowlist(pin_build, tuple(
        FieldPolicy(f, Visibility.PARTY, frozenset({'narrative_context'})) for f in FIELDS))

    args.db_dir.mkdir(parents=True, exist_ok=True)
    store = CampaignStore.open(args.db_dir / f'{args.campaign}.sqlite3', args.campaign)
    recorder = ObservationRecorder(store)
    print(f'db {args.db_dir / (args.campaign + ".sqlite3")} active branch {recorder.branch_id}')

    bridge: ReadOnlyBridge | None = None
    skipped: Counter[str] = Counter()
    deadline = time.monotonic() + args.duration
    while time.monotonic() < deadline:
        if bridge is None or not bridge.session_check.ok:
            text, age = source.fetch()
            snap = parse_latest_snapshot(text) if age <= 10 else None
            epoch = snap.session_seq if snap else 0
            bridge = ReadOnlyBridge(
                SessionIdentity(args.campaign, 'main', epoch, pin_build, pin_modpack,
                                ADAPTER_VERSION), allowlist, adapter,
                evidence=Evidence.LAB_OBSERVED)
            check = bridge.connect()
            print(f'{now_iso()} connect epoch={epoch} ok={check.ok} '
                  f'{[r.value for r in check.reasons] or ""}')
        envs = [bridge.handle({'operation': 'read', 'field': f, 'purpose': 'narrative_context',
                               'audience': 'PLAYER'}) for f in FIELDS]
        result = recorder.observe(*envs)
        if result.action is RecordAction.RECORDED:
            summary = ', '.join(f'{e.event_type}({e.payload.get("area") or e.payload.get("members") or ""})'
                                for e in result.events)
            print(f'{now_iso()} branch={result.branch_id} t={envs[1].value} {summary} '
                  f'+{result.experiences} memorias')
        elif result.action is RecordAction.SKIPPED:
            skipped[result.reason] += 1
        time.sleep(args.interval)

    print('\n--- resumo')
    print(f'pulados (sem observacao utilizavel): {dict(skipped)}')
    conn = store.connection
    for row in conn.execute('SELECT branch_id, parent_branch_id, fork_game_time, lineage '
                            'FROM branches ORDER BY rowid'):
        print(f'branch {row}')
    for row in conn.execute('SELECT branch_id, event_type, COUNT(*) FROM events '
                            'GROUP BY branch_id, event_type ORDER BY MIN(seq)'):
        print(f'eventos {row}')
    memory = MemoryStore(store)
    npcs = [n for (n,) in conn.execute('SELECT DISTINCT npc_id FROM npc_experiences')]
    for npc in npcs:
        recalled = memory.recall(npc_id=npc, branch_id=recorder.branch_id, at_game_time=10**9,
                                 purpose='npc_dialogue', audience='NARRATIVE_CONTEXT')
        items = [(i.claim_type, i.claim_payload.get('area') or i.claim_payload.get('members'),
                  i.experience.game_time) for i in recalled.items]
        print(f'recall {npc} (branch ativo): {items}')
    info = backup(store, args.db_dir / 'backups')
    check = verify_restore(info)
    print(f'backup {info.path.name} last_seq={info.last_seq} counts={info.counts} '
          f'verificado={check.ok} {check.problems or ""}')
    end = live_manifest(ssh, args.game_root, out_name='s1-live-manifest.json')
    print(f'build/modpack inalterados: {(build_fingerprint(end), modpack_hash(end)) == (live_build, live_modpack)}')
    store.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
