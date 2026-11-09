# SPDX-License-Identifier: Apache-2.0
"""S1b lab dialogue service: keeps the campaign DB current from the game and answers the overlay.

Lab-only (CR-2026-001, ADR-0113). One thread reads the game over SSH (bridge -> recorder, same as
the S1 session); an HTTP server bound to the VMware NAT address answers the Windows overlay.
Every request needs the session token. No endpoint writes to the game; transcripts are not
stored, and the console log carries metadata only (ADR-0107 item 6).

  export INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
  python tools/windows-lab/dialogue_service.py --pinned-manifest <manifest.json> --config-out <overlay.json>
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
import secrets
import sys
import threading
import time
from dataclasses import dataclass, field, replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
from infinity_ai.dialogue.context import Catalog, current_companions  # noqa: E402
from infinity_ai.dialogue.engine import DialogueEngine, DialogueRequest  # noqa: E402
from infinity_ai.dialogue.llm import OllamaProvider  # noqa: E402
from infinity_ai.state.recorder import ObservationRecorder, RecordAction  # noqa: E402
from infinity_ai.state.store import CampaignStore  # noqa: E402
from lab_ssh import SshLogSource, live_manifest, now_iso, ssh_from_env  # noqa: E402

FIELDS = (AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD)
MAX_BODY = 4096


@dataclass(frozen=True)
class GameView:
    observed: bool = False
    branch_id: str | None = None
    game_time: int | None = None
    area: str | None = None
    updated: str = ''
    companions: tuple[str, ...] = field(default_factory=tuple)


class Observer(threading.Thread):
    """Owns its own DB connection (SQLite connections are per thread)."""

    def __init__(self, args, ssh, pin_build, pin_modpack, live_build, live_modpack) -> None:
        super().__init__(daemon=True)
        self.args, self.ssh = args, ssh
        self.pin = (pin_build, pin_modpack)
        self.source = SshLogSource(ssh, args.game_root)
        self.adapter = EEexLogAdapter(self.source, campaign_id=args.campaign, branch_id='main',
                                      build_fingerprint=live_build, modpack_hash=live_modpack)
        self.allowlist = Allowlist(pin_build, tuple(
            FieldPolicy(f, Visibility.PARTY, frozenset({'narrative_context'})) for f in FIELDS))
        self.lock = threading.Lock()
        self.view = GameView()

    def snapshot(self) -> GameView:
        with self.lock:
            return self.view

    def run(self) -> None:
        store = CampaignStore.open(self.args.db, self.args.campaign)
        recorder = ObservationRecorder(store)
        bridge = None
        while True:
            try:
                if bridge is None or not bridge.session_check.ok:
                    text, age = self.source.fetch()
                    snap = parse_latest_snapshot(text) if age <= 10 else None
                    bridge = ReadOnlyBridge(
                        SessionIdentity(self.args.campaign, 'main', snap.session_seq if snap else 0,
                                        *self.pin, ADAPTER_VERSION),
                        self.allowlist, self.adapter, evidence=Evidence.LAB_OBSERVED)
                    bridge.connect()
                envs = [bridge.handle({'operation': 'read', 'field': f,
                                       'purpose': 'narrative_context', 'audience': 'PLAYER'})
                        for f in FIELDS]
                result = recorder.observe(*envs)
                if result.action is RecordAction.RECORDED:
                    print(f'{now_iso()} gravado: ' + ', '.join(e.event_type for e in result.events))
                observed = result.action is not RecordAction.SKIPPED
                view = GameView(
                    observed=observed, branch_id=recorder.branch_id,
                    game_time=int(envs[1].value) if observed else None,
                    area=envs[0].value if observed else None, updated=now_iso(),
                    companions=current_companions(store, recorder.branch_id) or ())
                with self.lock:
                    self.view = view
            except Exception as exc:  # keep observing; a failed poll just marks the view stale
                print(f'{now_iso()} observacao falhou: {type(exc).__name__}')
                with self.lock:
                    self.view = replace(self.view, observed=False)
            time.sleep(self.args.interval)


def make_handler(token: str, observer: Observer, catalog: Catalog, args):
    provider = OllamaProvider(args.model, base_url=args.ollama_url)

    class Handler(BaseHTTPRequestHandler):
        server_version = 'InfinityAIDialogue/0.1'

        def log_message(self, fmt, *a):  # no request lines with paths/addresses in the console
            pass

        def _send(self, status: int, doc: dict) -> None:
            body = json.dumps(doc, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def _authorized(self) -> bool:
            header = self.headers.get('Authorization', '')
            ok = header.startswith('Bearer ') and hmac.compare_digest(header[7:], token)
            if not ok:
                self._send(401, {'error': 'unauthorized'})
            return ok

        def do_GET(self) -> None:
            if not self._authorized():
                return
            if self.path != '/v1/state':
                return self._send(404, {'error': 'not found'})
            view = observer.snapshot()
            self._send(200, {
                'observed': view.observed,
                'area': catalog.area(view.area) if view.area else None,
                'companions': [{'npc_id': n, 'display_name': catalog.display(n)}
                               for n in view.companions],
                'updated': view.updated})

        def do_POST(self) -> None:
            if not self._authorized():
                return
            if self.path != '/v1/dialogue':
                return self._send(404, {'error': 'not found'})
            length = int(self.headers.get('Content-Length') or 0)
            if length <= 0 or length > MAX_BODY:
                return self._send(413, {'error': 'body size'})
            try:
                doc = json.loads(self.rfile.read(length).decode('utf-8'))
                npc_id, text = doc['npc_id'], doc['text']
            except (ValueError, KeyError, TypeError, UnicodeDecodeError):
                return self._send(400, {'error': 'bad request'})
            view = observer.snapshot()
            if not view.observed or view.branch_id is None:
                return self._send(200, {'status': 'DENIED', 'reason': 'NO_OBSERVATION',
                                        'speech': '', 'display_name': catalog.display(str(npc_id))})
            store = CampaignStore.open(args.db, args.campaign)
            try:
                result = DialogueEngine(store, provider, catalog).respond(
                    DialogueRequest(npc_id, text), branch_id=view.branch_id,
                    at_game_time=view.game_time)
            finally:
                store.close()
            print(f'{now_iso()} dialogo npc={result.npc_id} status={result.status.value} '
                  f'motivo={result.reason} fatos={len(result.used_event_ids)} '
                  f'nao_sabe={result.unknown} {result.latency_ms}ms flags={list(result.flags)}')
            self._send(200, {k: v for k, v in result.to_json().items()
                             if k in ('status', 'npc_id', 'display_name', 'speech', 'reason',
                                      'unknown', 'latency_ms')})

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--pinned-manifest', required=True, type=Path)
    ap.add_argument('--config-out', required=True, type=Path,
                    help='where to write the overlay config (URL + token) for copying to the VM')
    ap.add_argument('--campaign', default='lab-s1')
    ap.add_argument('--db', type=Path,
                    default=Path.home() / '.infinity-ai' / 'campaigns' / 'lab-s1.sqlite3')
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    ap.add_argument('--bind', default='192.168.150.1')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--model', default='qwen3:8b')
    ap.add_argument('--ollama-url', default='http://127.0.0.1:11434')
    ap.add_argument('--reuse-token', action='store_true',
                    help='keep the token already in --config-out (overlay keeps working after a restart)')
    ap.add_argument('--interval', type=float, default=3.0)
    args = ap.parse_args()

    pinned = json.loads(args.pinned_manifest.read_text(encoding='utf-8-sig'))
    pin_build, pin_modpack = build_fingerprint(pinned), modpack_hash(pinned)
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    live = live_manifest(ssh, args.game_root, out_name='s1b-live-manifest.json')
    live_build, live_modpack = build_fingerprint(live), modpack_hash(live)
    print(f'live matches pinned: {(live_build, live_modpack) == (pin_build, pin_modpack)}')

    observer = Observer(args, ssh, pin_build, pin_modpack, live_build, live_modpack)
    observer.start()

    token = secrets.token_urlsafe(24)
    if args.reuse_token and args.config_out.exists():
        token = json.loads(args.config_out.read_text(encoding='utf-8'))['token']
    args.config_out.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.config_out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
        json.dump({'url': f'http://{args.bind}:{args.port}', 'token': token}, fh)
    server = ThreadingHTTPServer((args.bind, args.port),
                                 make_handler(token, observer, Catalog.load(), args))
    print(f'servindo em http://{args.bind}:{args.port} (config do overlay em {args.config_out})')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
