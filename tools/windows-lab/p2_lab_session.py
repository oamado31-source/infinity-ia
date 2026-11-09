# SPDX-License-Identifier: Apache-2.0
"""P2 lab session: drive the read-only bridge against the EEex probe log on the Windows lab VM.

Lab-only helper (CR-2026-001). It reads over SSH; it never writes to the game folder.

  export INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
  python tools/windows-lab/p2_lab_session.py --pinned-manifest <p2-manifest.json> \
      --out <evidence.jsonl> --duration 120

The pinned manifest is the one collected right after installing the probe. The live manifest is
collected at start (and at the end) by the read-only P0 collector already copied to the VM.
The operator stands in for the host when (re)pinning the epoch after a load: each re-pin is logged.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.bridge.domain import (  # noqa: E402
    Allowlist, Evidence, FieldPolicy, SessionIdentity, Visibility,
)
from infinity_ai.bridge.eeex_log import (  # noqa: E402
    ADAPTER_VERSION, AREA_FIELD, GAME_TIME_FIELD, EEexLogAdapter, parse_latest_snapshot,
)
from infinity_ai.bridge.manifest import build_fingerprint, modpack_hash  # noqa: E402
from infinity_ai.bridge.service import ReadOnlyBridge  # noqa: E402
from lab_ssh import SshLogSource, live_manifest, now_iso, ssh_from_env  # noqa: E402

CAMPAIGN, BRANCH = 'lab-p2', 'main'
FIELDS = (AREA_FIELD, GAME_TIME_FIELD)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--pinned-manifest', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--duration', type=float, default=60.0)
    ap.add_argument('--interval', type=float, default=4.0)
    args = ap.parse_args()

    pinned_manifest = json.loads(args.pinned_manifest.read_text(encoding='utf-8-sig'))
    pin_build, pin_modpack = build_fingerprint(pinned_manifest), modpack_hash(pinned_manifest)
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    live = live_manifest(ssh, args.game_root)
    live_build, live_modpack = build_fingerprint(live), modpack_hash(live)

    source = SshLogSource(ssh, args.game_root)
    adapter = EEexLogAdapter(source, campaign_id=CAMPAIGN, branch_id=BRANCH,
                             build_fingerprint=live_build, modpack_hash=live_modpack)
    allowlist = Allowlist(pin_build, tuple(
        FieldPolicy(f, Visibility.PARTY, frozenset({'narrative_context'})) for f in FIELDS))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out = args.out.open('a', encoding='utf-8')

    def record(kind: str, **data) -> None:
        out.write(json.dumps({'t': now_iso(), 'kind': kind, **data}, ensure_ascii=False) + '\n')
        out.flush()

    record('start', pinned={'build': pin_build, 'modpack': pin_modpack},
           live={'build': live_build, 'modpack': live_modpack}, adapter=ADAPTER_VERSION)
    print(f'pinned build {pin_build[:19]}… modpack {pin_modpack[:19]}…')
    print(f'live   build {live_build[:19]}… modpack {live_modpack[:19]}…')

    bridge: ReadOnlyBridge | None = None
    adversarial_done = False
    deadline = time.monotonic() + args.duration
    while time.monotonic() < deadline:
        if bridge is None or not bridge.session_check.ok:
            text, age = source.fetch()
            snap = parse_latest_snapshot(text) if age <= 10 else None
            epoch = snap.session_seq if snap else 0
            pinned = SessionIdentity(CAMPAIGN, BRANCH, epoch, pin_build, pin_modpack,
                                     ADAPTER_VERSION)
            bridge = ReadOnlyBridge(pinned, allowlist, adapter, evidence=Evidence.LAB_OBSERVED)
            check = bridge.connect()
            reasons = [r.value for r in check.reasons]
            record('connect', epoch=epoch, ok=check.ok, reasons=reasons, log_age_s=age)
            print(f'connect epoch={epoch} ok={check.ok} {reasons or ""} log_age={age:.1f}s')

        if not adversarial_done and bridge.session_check.ok:
            for request in ({'operation': 'write', 'field': AREA_FIELD, 'value': 'AR0001'},
                            {'operation': 'read', 'field': 'creature.inventory',
                             'purpose': 'narrative_context', 'audience': 'PLAYER'},
                            {'operation': 'read', 'field': AREA_FIELD, 'purpose': 'marketing',
                             'audience': 'PLAYER'},
                            {'operation': 'read', 'field': AREA_FIELD,
                             'purpose': 'narrative_context', 'audience': 'ADMIN'}):
                env = bridge.handle(request).to_json()
                record('adversarial', request=request, envelope=env)
                print(f'  adversarial {request.get("operation")}/{request.get("field")}: '
                      f'{env["status"]} {env["reason"]}')
            adversarial_done = True

        cells = []
        for field in FIELDS:
            env = bridge.handle({'operation': 'read', 'field': field,
                                 'purpose': 'narrative_context', 'audience': 'PLAYER'}).to_json()
            record('observe', envelope=env)
            cells.append(f'{field.split(".")[-1]}={env["value"]} [{env["status"]}/{env["reason"]}]')
        print(f'{now_iso()} epoch={bridge.session_check.ok and "ok" or "closed"} ' +
              ' '.join(cells))
        time.sleep(args.interval)

    end_live = live_manifest(ssh, args.game_root)
    record('end', live_build=build_fingerprint(end_live), live_modpack=modpack_hash(end_live))
    print(f'end build unchanged: {build_fingerprint(end_live) == live_build}, '
          f'modpack unchanged: {modpack_hash(end_live) == live_modpack}')
    out.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
