# SPDX-License-Identifier: Apache-2.0
"""S1b lab dialogue service: keeps the campaign DB current from the game and answers the overlay.

Lab-only (CR-2026-001, ADR-0113). One thread reads the game over SSH (bridge -> recorder, same as
the S1 session); an HTTP server bound to the VMware NAT address answers the Windows overlay.
Every request needs the session token. No endpoint writes to the game; transcripts are not
stored, and the console log carries metadata only (ADR-0107 item 6). After each observation the
ADR-0114 rule runs on the pinned 1369 DR pack (pin it with pin_canon_pack.py; nothing is acquired
while the pin does not match). Companions never learn by time spent in a place. Locals placed by
the game data know their region's common knowledge (ADR-0116). In the in-game box (M_INFAIT.lua)
the player can talk to anyone alive: the request is recorded as NpcDialogueStarted, SPEC-006 gives
the person a profile (temporary for generic people, none for script-named ones), the reply goes
back through override/INFAIRSP.lua, and companions in earshot learn the entries a local actually
used (INQUIRY).

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
from infinity_ai.bridge.talk import (  # noqa: E402
    PLACEHOLDER_REPLY, REPLY_RESREF, parse_talk_requests, render_reply,
)
from infinity_ai.canon.pack import load_partition, load_sources  # noqa: E402
from infinity_ai.dialogue.context import (  # noqa: E402
    RESIDENT_FALLBACK, UNNAMED_AREA, Catalog, current_companions,
)
from infinity_ai.dialogue.engine import (  # noqa: E402
    DialogueEngine, DialogueRequest, DialogueStatus, ResidentRequest,
)
from infinity_ai.dialogue.llm import OllamaProvider  # noqa: E402
from infinity_ai.gamedata.inventory import (  # noqa: E402
    load_local_names, load_local_residents, load_local_resrefs,
)
from infinity_ai.memory.common_knowledge import (  # noqa: E402
    DEFAULT_RESIDENCE_THRESHOLD, acquire_common_knowledge, entries_named, identity_entries,
    placement_regions, relationship_entries, residents_as_stays, share_knowledge,
)
from infinity_ai.canon.pin import PinStatus, check_pin  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.personality import (  # noqa: E402
    FirstContactError, FirstContactService, NpcEncounterDialogue,
)
from infinity_ai.personality.identity import (  # noqa: E402
    build_identity, generate_identity, knowledge_tier, layered_text, load_curations,
    role_from_name,
)
from infinity_ai.personality.in_game import (  # noqa: E402
    profile_for, record_dialogue_start, resolve_speaker,
)
from infinity_ai.state.recorder import ObservationRecorder, RecordAction  # noqa: E402
from infinity_ai.state.store import CampaignStore  # noqa: E402
from lab_ssh import (  # noqa: E402
    SshLogSource, live_manifest, now_iso, put_override_file, ssh_from_env,
)

FIELDS = (AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD)
PENDING_WINDOW_MS = 55_000   # the in-game box gives up after 60 s
MAX_BODY = 4096


@dataclass(frozen=True)
class GameView:
    observed: bool = False
    branch_id: str | None = None
    game_time: int | None = None
    area: str | None = None
    updated: str = ''
    companions: tuple[str, ...] = field(default_factory=tuple)


class TeeLogSource:
    """Keeps the last log text fetched by the observer, so the talk thread needs no extra SSH."""

    def __init__(self, inner) -> None:
        self._inner, self._lock, self._text = inner, threading.Lock(), ''

    def fetch(self) -> tuple[str, float]:
        text, age = self._inner.fetch()
        with self._lock:
            self._text = text
        return text, age

    def last_text(self) -> str:
        with self._lock:
            return self._text


class Observer(threading.Thread):
    """Owns its own DB connection (SQLite connections are per thread)."""

    def __init__(self, args, ssh, pin_build, pin_modpack, live_build, live_modpack,
                 catalog: Catalog | None = None) -> None:
        super().__init__(daemon=True)
        self.args, self.ssh = args, ssh
        self.catalog = catalog or Catalog.load()
        self.pack = load_partition(args.campaign_year)
        self.sources = load_sources()
        self.build_areas = load_local_resrefs(live_build, args.language)
        self.residents = load_local_residents(live_build, args.language)
        self.stays = residents_as_stays(self.pack, self.residents, live_build)
        self.curations = load_curations(self.pack)
        self._knowledge_status = None
        self.pin = (pin_build, pin_modpack)
        self.source = TeeLogSource(SshLogSource(ssh, args.game_root))
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
                if observed:
                    self._acquire(store, recorder.branch_id, int(envs[1].value))
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


    def _acquire(self, store: CampaignStore, branch_id: str, game_time: int) -> None:
        report = acquire_common_knowledge(
            store, branch_id, self.pack, campaign_year=self.args.campaign_year,
            build_areas=self.build_areas, backgrounds=self.catalog.backgrounds(),
            residents=self.stays, threshold=self.args.residence_threshold, at_game_time=game_time,
            sources=self.sources)
        if report.status != self._knowledge_status:
            print(f'{now_iso()} conhecimento comum: {report.status}')
            self._knowledge_status = report.status
        for k in report.granted:
            print(f'{now_iso()} conhecimento comum adquirido: npc={k.npc_id} entrada={k.entry_id} '
                  f'base={k.basis.value} regiao={k.region_id} t={k.game_time}')


class Talker(threading.Thread):
    """Answers the in-game box (INFAI-TALK lines) as a local resident and applies INQUIRY."""

    def __init__(self, args, ssh, observer: Observer, catalog: Catalog) -> None:
        super().__init__(daemon=True)
        self.args, self.ssh, self.observer, self.catalog = args, ssh, observer, catalog
        self.provider = OllamaProvider(args.model, base_url=args.ollama_url)
        self.seen: set[str] | None = None
        self._lock = threading.Lock()
        self._last: dict | None = None      # last box exchange, in memory only (overlay fallback)

    def last_exchange(self) -> dict | None:
        with self._lock:
            return dict(self._last) if self._last else None

    def run(self) -> None:
        store = CampaignStore.open(self.args.db, self.args.campaign)
        while True:
            try:
                text = self.observer.source.last_text()
                requests = parse_talk_requests(text) if text else []
                if self.seen is None:
                    # Old requests are not replayed, but one the box is still waiting for (same
                    # session, under the box timeout, never answered) is, e.g. after a restart.
                    if text:
                        snap = parse_latest_snapshot(text)
                        answered = {json.loads(row[0]).get('req_id') for row in
                                    store.connection.execute(
                                        "SELECT payload_json FROM events "
                                        "WHERE event_type = 'NpcDialogueStarted'")}
                        self.seen = {r.req_id for r in requests if r.req_id in answered or not (
                            snap and r.session_seq == snap.session_seq
                            and 0 <= snap.clock_ms - r.clock_ms <= PENDING_WINDOW_MS)}
                elif self.observer.snapshot().observed:      # wait for the first observation
                    for req in requests:
                        if req.req_id not in self.seen:
                            self.seen.add(req.req_id)
                            self._answer(store, req)
            except Exception as exc:  # keep answering; one failed request is just logged
                print(f'{now_iso()} caixa de dialogo falhou: {type(exc).__name__}')
            time.sleep(0.5)

    def _answer(self, store: CampaignStore, req) -> None:
        view = self.observer.snapshot()
        speaker = resolve_speaker(req, self.observer.residents) or ''
        resident = self.observer.residents.get(speaker)
        areas = resident.areas if resident is not None and speaker in self.observer.stays else ()
        scope, shared, ident_source = '-', '-', '-'
        known_by_identity, known_by_relationship, known_now = [], [], ()
        flags: list[str] = []
        wisdom = intelligence = None
        tier, known_texts = '-', {}
        if not view.observed or view.branch_id is None or view.game_time is None:
            speech, status, reason, used, granted = RESIDENT_FALLBACK, 'DENIED', 'NO_OBSERVATION', (), ()
        else:
            # SPEC-006: the box request is the dialogue-start observation (no text stored).
            started = record_dialogue_start(store, view.branch_id, req, game_time=view.game_time,
                                            speaker_id=speaker or None)
            pack = self.observer.pack
            homes = placement_regions(pack, req.area) if areas and req.area else []
            home = homes[0] if homes else None
            gender = getattr(resident, 'gender', 0)

            def background(generated_id: str) -> dict:   # ADR-0117, generic people only
                return generate_identity(
                    npc_id=generated_id, role=role_from_name(req.speaker_name), gender=gender,
                    home_region=home, pack=pack, world_seed=self.args.world_seed,
                    campaign_id=store.campaign_id, branch_id=view.branch_id)

            profile, scope, generated = profile_for(
                store, view.branch_id, started, at_game_time=view.game_time,
                world_seed=self.args.world_seed, identity_factory=background)
            place = self.catalog.area(req.area) if home else None
            curation = self.observer.curations.get(speaker)
            identity = build_identity(
                npc_id=speaker or 'npc:desconhecido', name=req.speaker_name, pack=pack,
                place=place if place != UNNAMED_AREA else None, home_region=home,
                resident=resident, curation=curation, generated=generated)
            ident_source = identity.source
            # ADR-0117: public knowledge from homeland/home; ADR-0119: private edges by affiliation.
            if check_pin(store, view.branch_id, pack) is PinStatus.MATCH:
                known_by_identity = identity_entries(
                    pack, homeland=identity.origin_region, home=identity.home_region,
                    campaign_year=self.args.campaign_year, build_areas=self.observer.build_areas)
                known_by_relationship = relationship_entries(
                    pack, npc_id=speaker, affiliations=curation.affiliations if curation else (),
                    campaign_year=self.args.campaign_year, build_areas=self.observer.build_areas)
            stored = set(MemoryStore(store).known_canon(speaker, view.branch_id, view.game_time)) \
                if speaker else set()
            known_now = tuple(sorted(stored | set(known_by_identity) | set(known_by_relationship)))
            also_known = tuple((e, pack.get(e).title, pack.get(e).summary, pack.get(e).layers)
                               for e in known_now if pack.get(e) is not None)
            # Wisdom and Intelligence (game data) set how deeply the person knows (ADR-0117).
            wisdom = getattr(resident, 'wisdom', 0) or None
            intelligence = getattr(resident, 'intelligence', 0) or None
            tier_obj = knowledge_tier(wisdom, intelligence)
            tier = tier_obj.name
            known_texts = {e: layered_text(pack.get(e).summary, pack.get(e).layers, tier_obj)
                           for e in known_now if pack.get(e) is not None}
            result = DialogueEngine(store, self.provider, self.catalog).respond_resident(
                ResidentRequest(speaker, req.speaker_name, req.text, req.area, req.speaker_dead),
                residence_areas=areas, branch_id=view.branch_id, at_game_time=view.game_time,
                profile=profile, identity=identity, also_known=also_known, wisdom=wisdom,
                intelligence=intelligence, game_alignment=getattr(resident, 'alignment', None))
            status, reason = result.status.value, result.reason
            flags = list(result.flags)
            speech = result.speech or ('...' if req.speaker_dead else RESIDENT_FALLBACK)
            used = tuple(e.split(':', 1)[1] for e in result.used_event_ids
                         if e.startswith('canon:'))
            if result.status is DialogueStatus.OK and speaker:
                # The model may name an entry without declaring it: what was said is what was heard.
                used = tuple(dict.fromkeys(used + tuple(entries_named(
                    self.observer.pack, known_now, speech, known_texts, question=req.text))))
            granted = ()
            shareable = tuple(e for e in used if pack.get(e) is not None
                              and pack.get(e).access_scope == 'COMMON_REGIONAL')
            if result.status is DialogueStatus.OK and shareable and req.listeners:
                report = share_knowledge(
                    store, view.branch_id, self.observer.pack, speaker=speaker,
                    listeners=req.listeners, used_entry_ids=shareable, req_id=req.req_id,
                    host_epoch=req.session_seq, at_game_time=view.game_time, speech=speech,
                    also_held=known_by_identity, known_texts=known_texts, question=req.text)
                granted = report.granted
                shared = report.status + ''.join(f' {r.entry_id}:{r.reason}' for r in report.refusals
                                                 if r.reason != 'NOT_A_LISTENER')
        with self._lock:
            self._last = {'req_id': req.req_id, 'speaker': req.speaker_name, 'question': req.text,
                          'speech': speech}
        put_override_file(self.ssh, self.args.game_root, f'{REPLY_RESREF}.lua',
                          render_reply(req.req_id, speech).encode('utf-8'))
        print(f'{now_iso()} caixa pedido={req.req_id} falante={speaker or "-"} '
              f'habitante={bool(areas)} perfil={scope} identidade={ident_source} '
              f'wis={wisdom or "-"} int={intelligence or "-"} camada={tier} '
              f'assuntos={len(known_now)} recusas={flags} '
              f'status={status} motivo={reason} '
              f'entradas={list(used)} inquiry={shared} '
              f'ouvintes={list(req.listeners) if req.listeners is not None else None}')
        for k in granted:
            print(f'{now_iso()} conhecimento comum adquirido: npc={k.npc_id} entrada={k.entry_id} '
                  f'base={k.basis.value} regiao={k.region_id} t={k.game_time}')


def make_handler(token: str, observer: Observer, catalog: Catalog, args, talker=None):
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
                'box': talker.last_exchange() if talker else None,
                'updated': view.updated})

        def do_POST(self) -> None:
            if not self._authorized():
                return
            if self.path not in ('/v1/dialogue', '/v1/encounter-dialogue'):
                return self._send(404, {'error': 'not found'})
            length = int(self.headers.get('Content-Length') or 0)
            if length <= 0 or length > MAX_BODY:
                return self._send(413, {'error': 'body size'})
            try:
                doc = json.loads(self.rfile.read(length).decode('utf-8'))
                text = doc['text']
                npc_id = doc['npc_id'] if self.path == '/v1/dialogue' else None
                contact_event_id = (doc.get('contact_event_id')
                                    if self.path == '/v1/encounter-dialogue' else None)
            except (ValueError, KeyError, TypeError, UnicodeDecodeError):
                return self._send(400, {'error': 'bad request'})
            view = observer.snapshot()
            if not view.observed or view.branch_id is None:
                return self._send(200, {'status': 'DENIED', 'reason': 'NO_OBSERVATION',
                                        'speech': '',
                                        'display_name': catalog.display(npc_id) if npc_id
                                        else 'Pessoa desconhecida'})
            store = CampaignStore.open(args.db, args.campaign)
            try:
                if self.path == '/v1/encounter-dialogue':
                    # The client sends ONLY a reference to an already recorded trusted
                    # observation. It cannot invent role/identity/position or mark
                    # actors VERIFIED through this endpoint.
                    try:
                        if not isinstance(contact_event_id, str) or not contact_event_id:
                            raise FirstContactError('CONTACT_OBSERVATION_REQUIRED')
                        event = store.get_event(contact_event_id)
                        if not event or event.payload.get('scene_id') != view.area:
                            raise FirstContactError('CONTACT_SCENE_MISMATCH')
                        contact = FirstContactService(store, world_seed=args.world_seed).begin(
                            contact_event_id=contact_event_id, branch_id=view.branch_id,
                            at_game_time=view.game_time)
                    except FirstContactError as exc:
                        return self._send(200, {'status': 'DENIED',
                                                'reason': str(exc), 'speech': '',
                                                'display_name': 'Pessoa desconhecida'})
                    result = NpcEncounterDialogue(provider).respond(contact, text)
                else:
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
    ap.add_argument('--world-seed', default='lab-s1',
                    help='stable per-campaign SPEC-006 seed; not a game-derived identity')
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
    ap.add_argument('--language', default='pt_BR', help='game language of the local area inventory')
    ap.add_argument('--campaign-year', type=int, default=1369, help='DR year (ADR-0109)')
    ap.add_argument('--residence-threshold', type=int, default=DEFAULT_RESIDENCE_THRESHOLD,
                    help='game time an NPC outside the party lives in a region before it knows its '
                         'common knowledge (ADR-0114; party members never learn by time)')
    args = ap.parse_args()

    pinned = json.loads(args.pinned_manifest.read_text(encoding='utf-8-sig'))
    pin_build, pin_modpack = build_fingerprint(pinned), modpack_hash(pinned)
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    live = live_manifest(ssh, args.game_root, out_name='s1b-live-manifest.json')
    live_build, live_modpack = build_fingerprint(live), modpack_hash(live)
    print(f'live matches pinned: {(live_build, live_modpack) == (pin_build, pin_modpack)}')

    game_names = load_local_names(live_build, args.language)
    print(f'nomes de area do jogo (inventario local): {len(game_names)}')
    catalog = Catalog.load(game_area_names=game_names)
    observer = Observer(args, ssh, pin_build, pin_modpack, live_build, live_modpack, catalog)
    print(f'pacote {args.campaign_year} DR {observer.pack.revision[:19]}..., '
          f'areas da build: {len(observer.build_areas or ())}, '
          f'habitantes locais: {len(observer.stays)}, '
          f'identidades curadas: {len(observer.curations)}, '
          f'limite de residencia: {args.residence_threshold}')
    CampaignStore.open(args.db, args.campaign).close()   # migrate once before the threads open it
    # The reply file must exist when the game starts, or Infinity_DoFile never finds it.
    put_override_file(ssh, args.game_root, f'{REPLY_RESREF}.lua', PLACEHOLDER_REPLY.encode('utf-8'))
    observer.start()
    talker = Talker(args, ssh, observer, catalog)
    talker.start()

    token = secrets.token_urlsafe(24)
    if args.reuse_token and args.config_out.exists():
        token = json.loads(args.config_out.read_text(encoding='utf-8'))['token']
    args.config_out.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.config_out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
        json.dump({'url': f'http://{args.bind}:{args.port}', 'token': token}, fh)
    server = ThreadingHTTPServer((args.bind, args.port), make_handler(
        token, observer, catalog, args, talker))
    print(f'servindo em http://{args.bind}:{args.port} (config do overlay em {args.config_out})')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        put_override_file(ssh, args.game_root, f'{REPLY_RESREF}.lua',
                          PLACEHOLDER_REPLY.encode('utf-8'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
