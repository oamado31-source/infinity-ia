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
import atexit
import hmac
import json
import math
import os
import re
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
    PLACEHOLDER_PTT, PLACEHOLDER_QUEST, PLACEHOLDER_REPLY, PTT_RESREF, QUEST_RESREF, REPLY_RESREF,
    fresh_ptt_signals, parse_ptt_signals, parse_talk_requests, render_ptt_state,
    render_quest_probes, render_reply,
)
from infinity_ai.canon.pack import load_partition, load_sources  # noqa: E402
from infinity_ai.dialogue.context import (  # noqa: E402
    RESIDENT_FALLBACK, UNNAMED_AREA, Catalog, current_companions,
)
from infinity_ai.dialogue.engine import (  # noqa: E402
    DialogueEngine, DialogueRequest, DialogueStatus, ResidentRequest,
)
from infinity_ai.dialogue.conversation import ConversationMemory  # noqa: E402
from infinity_ai.dialogue.llm import OllamaProvider  # noqa: E402
from infinity_ai.dialogue.recall import (  # noqa: E402
    NO_RECALL, npc_key, recall, recall_lines, record_turn,
)
from infinity_ai.gamedata.inventory import (  # noqa: E402
    load_local_names, load_local_offers, load_local_residents, load_local_resrefs,
)
from infinity_ai.memory.common_knowledge import (  # noqa: E402
    DEFAULT_RESIDENCE_THRESHOLD, acquire_common_knowledge, common_words, context_order,
    entries_named,
    identity_knowledge, named_in,
    local_aliases, placement_regions, relationship_entries, residents_as_stays, share_knowledge,
)
from infinity_ai.canon.pin import PinStatus, carry_pin, check_pin  # noqa: E402
from infinity_ai.memory.model import KnowledgeBasis  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.personality import (  # noqa: E402
    FirstContactError, FirstContactService, NpcEncounterDialogue,
)
from infinity_ai.personality.identity import (  # noqa: E402
    HABITANTE, build_identity, generate_identity, knowledge_tier, layered_text, load_curations,
    place_in_district, popular_only, role_from_name,
)
from infinity_ai.personality.morale import (  # noqa: E402
    base_morale, classify_trigger, ethical_axis, modifiers, morale_for,
)
from infinity_ai.personality.reaction import reaction_for  # noqa: E402
from infinity_ai.personality.trust import revise_trust  # noqa: E402
from infinity_ai.quests.milestones import (  # noqa: E402
    DEFAULT_CATALOG, evaluate, load_catalog, record_milestones,
)
from infinity_ai.quests.clock import hour_of, is_night  # noqa: E402
from infinity_ai.quests.narrative import (  # noqa: E402
    advance, arrive, load_quests, mark_journal_shown, pending_journal, with_journal,
)
from infinity_ai.quests.presence import (  # noqa: E402
    arrival_plan, call_due, decide, dispatch, dispatch_call, open_passages, record_arrival,
)
from infinity_ai.actions.gateway import (  # noqa: E402
    ARR_RESREF, DOOR_RESREF, ActionRequest, parse_receipts, render_arrival_plan,
    render_passage_plan,
)
from infinity_ai.dialogue.disclosure import CLOSED_DISPOSITIONS  # noqa: E402
from infinity_ai.personality.in_game import (  # noqa: E402
    profile_for, record_dialogue_start, resolve_speaker,
)
from infinity_ai.state.recorder import ObservationRecorder, RecordAction  # noqa: E402
from infinity_ai.voice.capture import FfmpegRecorder  # noqa: E402
from infinity_ai.voice.session import VoiceSession  # noqa: E402
from infinity_ai.voice.stt import WhisperServerStt, vocabulary_prompt  # noqa: E402
from infinity_ai.state.store import CampaignStore  # noqa: E402
from lab_ssh import (  # noqa: E402
    OverrideWriter, RemoteShell, SshLogSource, grep_log, live_manifest, now_iso,
    put_override_file,
    ssh_from_env,
)

FIELDS = (AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD)
PENDING_WINDOW_MS = 55_000   # the in-game box gives up after 60 s
MAX_BODY = 4096
ARRIVAL_WAIT_S = 12.0        # ADR-0145: how long the module's arrival answers may take


@dataclass(frozen=True)
class GameView:
    observed: bool = False
    branch_id: str | None = None
    game_time: int | None = None
    area: str | None = None
    updated: str = ''
    companions: tuple[str, ...] = field(default_factory=tuple)


class TeeLogSource:
    """The last log text read from the game, shared by every thread (S1i latency). Only LogTail
    reads the game, over one long-lived shell, a few times a second; fetch() and last_text() return
    that copy, with its age advanced by the time since it was read."""

    def __init__(self, inner) -> None:
        self._inner, self._lock = inner, threading.Lock()
        self._text, self._age, self._at = '', math.inf, time.monotonic()

    def refresh(self) -> None:
        text, age = self._inner.fetch()
        with self._lock:
            self._text, self._age, self._at = text, age, time.monotonic()

    def fetch(self) -> tuple[str, float]:
        with self._lock:
            return self._text, self._age + (time.monotonic() - self._at)

    def last_text(self) -> str:
        with self._lock:
            return self._text

    @property
    def launch(self) -> str:
        """The game launch the log comes from (process start), '' when unknown."""
        return getattr(self._inner, 'launch', '') or ''


class LogTail(threading.Thread):
    """Reads the game log every `interval` seconds; a failed read is logged once until it recovers."""

    def __init__(self, source: TeeLogSource, interval: float) -> None:
        super().__init__(daemon=True)
        self.source, self.interval = source, interval

    def run(self) -> None:
        failing = False
        while True:
            try:
                self.source.refresh()
                if failing:
                    print(f'{now_iso()} leitura do log voltou')
                failing = False
            except Exception as exc:  # keep reading; the views just get older meanwhile
                if not failing:
                    print(f'{now_iso()} leitura do log falhou: {type(exc).__name__}')
                failing = True
                time.sleep(1.0)
            time.sleep(self.interval)


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
        self.offers = load_local_offers(live_build, args.language)   # ADR-0132: who sells what
        self.stays = residents_as_stays(self.pack, self.residents, live_build)
        self.curations = load_curations(self.pack)
        # ADR-0134: the local quest catalog (allowlist and curated meaning), outside the repo.
        self.live_build = live_build
        self.quest_catalog = load_catalog(args.quest_catalog)
        self.quests = load_quests()          # SPEC-011: curated narrative quests
        if getattr(args, "local_quests", None):   # lab only: test quests kept out of the repository
            self.quests.update({q: v for q, v in load_quests(args.local_quests).items()
                                if q not in self.quests})
        self._knowledge_status = None
        self._pin_warned: set[str] = set()
        self.pin = (pin_build, pin_modpack)
        self.source = TeeLogSource(SshLogSource(ssh, args.game_root, shell=RemoteShell(ssh)))
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
                if observed and envs[0].value:     # ADR-0139: arrival steps (no game write)
                    now_t = int(envs[1].value)
                    for done in arrive(store, recorder.branch_id, self.quests, area=envs[0].value,
                                       game_time=now_t, night=is_night(now_t)):
                        print(f'{now_iso()} chegada: {done} em {envs[0].value} '
                              f'(t={now_t}, hora {hour_of(now_t)})')
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
        if self.args.carry_pin:          # CR-2026-020: only a revision already pinned by hand
            carried = carry_pin(store, branch_id, self.pack, game_time=game_time)
            if carried:
                pin, source = carried
                print(f'{now_iso()} pin levado ao ramo {branch_id}: revisao '
                      f'{self.pack.revision[:19]}... ({len(self.pack.entries)} entradas, t={game_time}),'
                      f' aprovada no pin {source.event_id} do ramo {source.branch_id}')
        report = acquire_common_knowledge(
            store, branch_id, self.pack, campaign_year=self.args.campaign_year,
            build_areas=self.build_areas, backgrounds=self.catalog.backgrounds(),
            residents=self.stays, threshold=self.args.residence_threshold, at_game_time=game_time,
            sources=self.sources)
        if report.status != self._knowledge_status:
            print(f'{now_iso()} conhecimento comum: {report.status}')
            self._knowledge_status = report.status
        # Lab: loading an older save opens a branch that may carry an older pin, and the pack's
        # knowledge stays off there until a new explicit pin (REQ-REL-012). Say it once per branch.
        stale = report.status in ('REVISION_CHANGED', 'NOT_PINNED')
        if stale and branch_id not in self._pin_warned:
            self._pin_warned.add(branch_id)
            print(f'{now_iso()} AVISO: o ramo {branch_id} esta com o pacote {report.status}; o '
                  f'conhecimento do pacote fica desligado ali ate um novo pin: '
                  f'tools/windows-lab/pin_canon_pack.py --campaign {self.args.campaign} '
                  f'--db {self.args.db}')
        for k in report.granted:
            print(f'{now_iso()} conhecimento comum adquirido: npc={k.npc_id} entrada={k.entry_id} '
                  f'base={k.basis.value} regiao={k.region_id} t={k.game_time}')


class PresenceDirector(threading.Thread):
    """ADR-0138 (lab, `--quest-presence`): at each reading of the game, the quests decide who must
    be on the map and ask the action gateway once; what the game does not confirm is suspended."""

    def __init__(self, args, ssh, observer: Observer, fingerprint: str) -> None:
        super().__init__(daemon=True)
        self.args, self.ssh, self.observer, self.fingerprint = args, ssh, observer, fingerprint

    def run(self) -> None:
        from lab_action import SshTransport, deployed_templates
        store = CampaignStore.open(self.args.db, self.args.campaign)
        templates = deployed_templates(self.ssh, self.args.game_root, self.fingerprint)
        transport = SshTransport(self.ssh, self.args.game_root)
        print(f'{now_iso()} presenca por quest ligada: criaturas nossas instaladas '
              f'{sorted(templates)}')
        last_held: tuple[str, ...] = ()
        plan: dict[str, tuple] = {}          # ADR-0145: action_id -> (decision, request)
        written = None
        doors_written = None
        entered: tuple[str | None, float] = (None, 0.0)
        while True:
            try:
                view = self.observer.snapshot()
                if view.observed and view.branch_id and view.area and view.game_time is not None:
                    if entered[0] != view.area:
                        entered = (view.area, time.monotonic())
                    # ADR-0145: what the module made on entering this area, as the director would
                    here = {a: e for a, e in plan.items() if e[1].area == view.area}
                    answers = {}
                    for aid in here:
                        receipts = [r for r in parse_receipts('\n'.join(grep_log(
                            self.ssh, self.args.game_root, f'INFAI-ACT .*{aid}', limit=5)))
                            if r.action_id == aid and r.status in ('DONE', 'REFUSED')]
                        if receipts:
                            answers[aid] = receipts[-1]
                    if here and len(answers) == len(here):
                        made = sum(r.observed - r.before for r in answers.values()
                                   if r.status == 'DONE' and r.observed is not None
                                   and r.before is not None)
                        for aid, (dec, req) in here.items():
                            r = answers[aid]
                            state = record_arrival(store, view.branch_id, dec, req, r,
                                                   game_time=view.game_time, arrival_made=made)
                            print(f'{now_iso()} chegada preparada {dec.quest_id}/'
                                  f'{dec.presence.presence_id}: {r.before} -> {r.observed} em '
                                  f'{req.area} (area {r.seen_before} -> {r.seen}): {state}')
                            plan.pop(aid)
                    elif here and time.monotonic() - entered[1] > ARRIVAL_WAIT_S:
                        for aid, (dec, req) in here.items():   # some unanswered: record what came
                            if aid in answers:
                                record_arrival(store, view.branch_id, dec, req, answers[aid],
                                               game_time=view.game_time)
                            plan.pop(aid)                       # the director creates as before
                    if any(e[1].area == view.area for e in plan.values()):
                        time.sleep(1.0)
                        continue
                    wanted_now = arrival_plan(store, view.branch_id, self.observer.quests,
                                              area=view.area, game_time=view.game_time,
                                              templates=templates)
                    keep = {(d.quest_id, d.presence.presence_id, r.area, r.count): aid
                            for aid, (d, r) in plan.items()}
                    plan = {}
                    for d, r in wanted_now:
                        aid = keep.get((d.quest_id, d.presence.presence_id, r.area, r.count),
                                       r.action_id)
                        plan[aid] = (d, ActionRequest(aid, r.op, r.area, r.name, r.cre, r.x, r.y,
                                                      r.facing, r.count))
                    doors = render_passage_plan(open_passages(store, view.branch_id,
                                                              self.observer.quests))
                    if doors != doors_written:       # ADR-0146: the passages the quests opened
                        put_override_file(self.ssh, self.args.game_root, f'{DOOR_RESREF}.lua',
                                          doors.encode('utf-8'))
                        doors_written = doors
                        print(f'{now_iso()} passagens abertas: {doors.count("id = ")}')
                    text = render_arrival_plan([r for _, r in plan.values()])
                    if text != written:
                        put_override_file(self.ssh, self.args.game_root, f'{ARR_RESREF}.lua',
                                          text.encode('utf-8'))
                        written = text
                        print(f'{now_iso()} plano de chegada: '
                              f'{sorted((r.area, r.name, r.count) for _, r in plan.values())}')
                    decision, held = decide(store, view.branch_id, self.observer.quests,
                                            area=view.area, game_time=view.game_time)
                    if held != last_held and held:
                        print(f'{now_iso()} presenca retida: {list(held)} (lab_action.py resume)')
                    last_held = held
                    if decision is not None:
                        p = decision.presence
                        print(f'{now_iso()} presenca {decision.quest_id}/{p.presence_id}: '
                              f'{decision.rule} {p.cre if decision.rule == "ENTER" else p.name} '
                              f'em {p.area} (ramo {view.branch_id}, t={view.game_time}, '
                              f'hora {hour_of(view.game_time)})')
                        state = dispatch(store, view.branch_id, decision, transport=transport,
                                         templates=templates, game_time=view.game_time)
                        print(f'{now_iso()} presenca {decision.quest_id}/{p.presence_id}: {state}')
                    else:                        # ADR-0144: a giver calling for help, if due
                        quest = call_due(store, view.branch_id, self.observer.quests,
                                         area=view.area, game_time=view.game_time)
                        if quest is not None:
                            state = dispatch_call(store, view.branch_id, quest,
                                                  transport=transport, game_time=view.game_time)
                            print(f'{now_iso()} chamado {quest.quest_id}: '
                                  f'{quest.call.script_name} em {quest.call.area} '
                                  f'(frase {quest.call.strref}): {state}')
            except Exception as exc:  # keep directing; a failed round leaves its events as they are
                print(f'{now_iso()} presenca falhou: {type(exc).__name__}')
            time.sleep(max(self.args.interval, 2.0))


class VoiceListener(threading.Thread):
    """ADR-0127: push-to-talk for the in-game box. The microphone of this host opens on the box's
    START and closes on STOP/CANCEL or at the time limit; the local STT turns it into text that
    goes back to the box for review. Audio is deleted right away; the log has no transcript."""

    def __init__(self, args, ssh, observer: Observer, catalog: Catalog,
                 writer: OverrideWriter) -> None:
        super().__init__(daemon=True)
        self.args, self.ssh, self.observer, self.catalog = args, ssh, observer, catalog
        self.writer = writer
        # S1i: the STT server keeps the model loaded (falls back to whisper-cli per press).
        self.stt = WhisperServerStt(args.stt_model)
        threading.Thread(target=self.stt.start, daemon=True).start()
        atexit.register(self.stt.stop)
        self.session = VoiceSession(
            lambda: FfmpegRecorder(device=args.mic_device, max_seconds=args.max_voice_s + 2),
            self.stt, max_seconds=args.max_voice_s,
            min_level=args.min_voice_level, prompt=self.vocabulary)
        self.seen: set[tuple[str, str]] | None = None
        self._last_text: str | None = None      # the log copy already parsed (polled at 10 Hz)

    def vocabulary(self) -> str:
        """Public names that help the STT spell them (place, regions, organizations)."""
        public = [e for e in self.observer.pack.entries.values()
                  if e.access_scope == 'COMMON_REGIONAL']
        names = [self.catalog.area(self.observer.snapshot().area)]
        # A capitalised word in the middle of a sentence is a proper name ("... de Lehtinan").
        names += [m.group(1) for e in public for m in re.finditer(
            r"(?<=[\w,;] )([A-ZÀ-Ý][a-zà-ÿ'-]{3,})", e.summary)]
        names += [e.title.split(':')[0] for e in public]
        return vocabulary_prompt(n for n in names if n and n != UNNAMED_AREA)

    def _show(self, update) -> None:
        print(f'{now_iso()} voz {update.summary()}')
        if update.ptt_id:
            self.writer.put(f'{PTT_RESREF}.lua', render_ptt_state(
                update.ptt_id, update.state, update.text).encode('utf-8'))

    def run(self) -> None:
        while True:
            try:
                text = self.observer.source.last_text()
                changed, self._last_text = text is not self._last_text, text
                snap = parse_latest_snapshot(text) if text and changed else None
                if text and self.seen is None:
                    # Presses already in the log when the service starts are never acted on:
                    # the microphone opens only for a press made while it runs. Nothing is
                    # marked before the log was read at least once.
                    self.seen = {(s.ptt_id, s.action) for s in parse_ptt_signals(text)}
                elif text and snap is not None:
                    for s in fresh_ptt_signals(parse_ptt_signals(text), self.seen,
                                               session_seq=snap.session_seq,
                                               clock_ms=snap.clock_ms):
                        for update in self.session.handle(s.ptt_id, s.action):
                            self._show(update)
                for update in self.session.tick():
                    self._show(update)
            except Exception as exc:  # keep listening; a failed press is just logged
                print(f'{now_iso()} voz falhou: {type(exc).__name__}')
            time.sleep(0.1)


class Talker(threading.Thread):
    """Answers the in-game box (INFAI-TALK lines) as a local resident and applies INQUIRY."""

    def __init__(self, args, ssh, observer: Observer, catalog: Catalog,
                 writer: OverrideWriter) -> None:
        super().__init__(daemon=True)
        self.args, self.ssh, self.observer, self.catalog = args, ssh, observer, catalog
        self.writer = writer
        self.provider = OllamaProvider(args.model, base_url=args.ollama_url)
        self.seen: set[str] | None = None
        self._last_text: str | None = None      # the log copy already parsed (polled at 10 Hz)
        self._lock = threading.Lock()
        self._last: dict | None = None      # last box exchange, in memory only (overlay fallback)
        self.conversations = ConversationMemory()   # ADR-0123: turns of open boxes, RAM only

    def last_exchange(self) -> dict | None:
        with self._lock:
            return dict(self._last) if self._last else None

    def run(self) -> None:
        store = CampaignStore.open(self.args.db, self.args.campaign)
        while True:
            try:
                text = self.observer.source.last_text()
                if text is self._last_text and self.seen is not None:
                    time.sleep(0.1)
                    continue                      # nothing new in the log copy
                self._last_text = text
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
                        answered |= self._answered_companions()
                        self.seen = {r.req_id for r in requests if r.req_id in answered or not (
                            snap and r.session_seq == snap.session_seq
                            and 0 <= snap.clock_ms - r.clock_ms <= PENDING_WINDOW_MS)}
                elif self.observer.snapshot().observed:      # wait for the first observation
                    for req in requests:
                        if req.req_id not in self.seen:
                            self.seen.add(req.req_id)
                            self._answer(store, req)
                            if req.speaker_party:
                                self._remember_companion(req.req_id)
            except Exception as exc:  # keep answering; one failed request is just logged
                print(f'{now_iso()} caixa de dialogo falhou: {type(exc).__name__}')
            time.sleep(0.1)

    def _answered_path(self) -> Path:
        # A companion's turn records no event (no first contact), so answered ids are kept in a
        # local side file next to the campaign database: no text, only request ids.
        return Path(self.args.db).expanduser().with_suffix('.talk-answered.txt')

    def _answered_companions(self) -> set[str]:
        try:
            return set(self._answered_path().read_text(encoding='utf-8').split())
        except OSError:
            return set()

    def _remember_companion(self, req_id: str) -> None:
        try:
            with self._answered_path().open('a', encoding='utf-8') as f:
                f.write(req_id + '\n')
        except OSError:
            pass

    def _answer(self, store: CampaignStore, req) -> None:
        view = self.observer.snapshot()
        speaker = resolve_speaker(req, self.observer.residents) or ''
        resident = self.observer.residents.get(speaker)
        # ADR-0123: earlier turns of this box opening; the previous question helps INQUIRY tell
        # what "e quem é então?" refers to.
        conv_key = speaker or f'name:{req.speaker_name}'
        history = self.conversations.history(req.conversation_id, conv_key)
        question = ' '.join(filter(None, (history[-1][0] if history else '', req.text)))
        areas = resident.areas if resident is not None and speaker in self.observer.stays else ()
        curation = self.observer.curations.get(speaker)
        if not areas and resident is not None and curation is not None \
                and curation.standing == HABITANTE:
            areas = resident.areas      # ADR-0120: a checked curation says it lives here
        scope, shared, ident_source = '-', '-', '-'
        known_by_identity, known_by_relationship, known_now = [], [], ()
        flags: list[str] = []
        wisdom = intelligence = None
        tier, known_texts, standing = '-', {}, '-'
        trust = None
        reaction = check = None
        quests = None
        story = None          # SPEC-011: this turn of the narrative quests
        # ADR-0134: the box's reading of the allowlisted variables -> this branch's milestones.
        if view.branch_id is not None and self.observer.quest_catalog is not None:
            quests = record_milestones(
                store, view.branch_id, self.observer.quest_catalog,
                evaluate(self.observer.quest_catalog, req.probes, self.observer.live_build),
                game_time=view.game_time, host_epoch=req.session_seq or 0)
            if self.args.watch_probes:       # lab curation only (D4): never in the evidence
                print(f'{now_iso()} probes {dict(req.probes) if req.probes is not None else None}')
        # ADR-0124: earlier conversations with the player (ids and game time only).
        memory_key = npc_key(speaker, stable=bool(req.speaker_party or req.speaker_script
                                                   or curation is not None),
                             session_seq=req.session_seq, instance=req.speaker_instance)
        earlier = recall(store, view.branch_id, memory_key, at_game_time=view.game_time,
                         exclude_conversation=req.conversation_id) \
            if view.branch_id is not None else NO_RECALL
        pack_now = self.observer.pack
        lines = recall_lines(earlier, {e: pack_now.get(e).title for e in earlier.subjects
                                       if pack_now.get(e) is not None}, view.game_time)
        if not view.observed or view.branch_id is None or view.game_time is None:
            speech, status, reason, used, granted = RESIDENT_FALLBACK, 'DENIED', 'NO_OBSERVATION', (), ()
        elif req.speaker_party:
            # A companion in the box talks exactly as in the overlay: party memories and what it
            # learned (SPEC-004); no first contact, no INQUIRY (a companion never teaches another).
            # ADR-0117: its Wisdom/Intelligence (sent by the box) set the depth, as for residents.
            wisdom, intelligence = req.speaker_wisdom, req.speaker_intelligence
            if wisdom or intelligence:
                tier = knowledge_tier(wisdom, intelligence).name
            # CR-2026-014: what fills the prompt, by closeness to where the party is.
            pack = self.observer.pack
            where = placement_regions(pack, req.area) if req.area else []
            order = tuple(context_order(pack, pack.entries, npc_id=speaker, area=req.area,
                                        home_region=where[0] if where else None,
                                        named=named_in(pack, pack.entries, req.text,
                                                       local_aliases(pack, req.area))))
            result = DialogueEngine(store, self.provider, self.catalog).respond(
                DialogueRequest(speaker, req.text), branch_id=view.branch_id,
                at_game_time=view.game_time, wisdom=wisdom, intelligence=intelligence,
                history=history, recall_lines=lines, order=order)
            status, reason, flags = result.status.value, result.reason, list(result.flags)
            speech = result.speech or self.catalog.persona(speaker).fallback
            used = tuple(e.split(':', 1)[1] for e in result.used_event_ids
                         if e.startswith('canon:'))
            granted, scope = (), 'COMPANHEIRO'
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

            # CR-2026-010: an official NPC with a checked curation but no script name (Bernard)
            # keeps the alignment of its game sheet; generic people still draw theirs.
            profile, scope, generated = profile_for(
                store, view.branch_id, started, at_game_time=view.game_time,
                world_seed=self.args.world_seed, identity_factory=background,
                game_alignment=getattr(resident, 'alignment', None)
                if curation is not None else None)
            place = self.catalog.area(req.area) if home else None
            if place and place != UNNAMED_AREA:      # the district around it, when known
                place = place_in_district(place, local_aliases(pack, req.area).get('bairro'))
            identity = build_identity(
                npc_id=speaker or 'npc:desconhecido', name=req.speaker_name, pack=pack,
                place=place if place != UNNAMED_AREA else None, home_region=home,
                resident=resident, curation=curation, generated=generated)
            ident_source, standing = identity.source, identity.standing
            # ADR-0117/0120: public knowledge from homeland/home by standing; ADR-0119: private
            # edges by affiliation.
            shallow_ids: list[str] = []
            if check_pin(store, view.branch_id, pack) is PinStatus.MATCH:
                known_by_identity, shallow_ids = identity_knowledge(
                    pack, homeland=identity.origin_region, home=identity.home_region,
                    campaign_year=self.args.campaign_year, build_areas=self.observer.build_areas,
                    standing=standing, visited=identity.visited_regions)
                known_by_relationship = relationship_entries(
                    pack, npc_id=speaker, affiliations=curation.affiliations if curation else (),
                    campaign_year=self.args.campaign_year, build_areas=self.observer.build_areas)
            away = frozenset({KnowledgeBasis.RESIDENCE}) if standing != HABITANTE else frozenset()
            stored = set(MemoryStore(store).known_canon(speaker, view.branch_id, view.game_time,
                                                        exclude_basis=away)) \
                if speaker else set()
            shallow = frozenset(e for e in shallow_ids if e not in stored)
            known_now = tuple(sorted(stored | set(known_by_identity) | set(known_by_relationship)
                                     | shallow))
            also_known = tuple((e, pack.get(e).title, pack.get(e).summary, pack.get(e).layers,
                                pack.get(e).access_scope, pack.get(e).subject_id,
                                pack.get(e).secrecy)
                               for e in known_now if pack.get(e) is not None)
            # Wisdom and Intelligence (game data) set how deeply the person knows (ADR-0117).
            wisdom = getattr(resident, 'wisdom', 0) or None
            intelligence = getattr(resident, 'intelligence', 0) or None
            tier_obj = knowledge_tier(wisdom, intelligence)
            tier = tier_obj.name
            known_texts = {e: layered_text(pack.get(e).summary, pack.get(e).layers,
                                           popular_only(tier_obj) if e in shallow else tier_obj)
                           for e in known_now if pack.get(e) is not None}
            # ADR-0125: the encounter reaction, once per person per session, decided by code.
            leader = req.selected_leader
            reaction = reaction_for(
                store, view.branch_id, key=memory_key or speaker, session=req.session_seq,
                opening_text=req.text,
                charisma=leader.charisma_active if leader is not None else None,
                charisma_of=(leader.script_name or leader.display_name)
                if leader is not None else '',
                world_seed=self.args.world_seed, game_time=view.game_time,
                launch=self.observer.source.launch)
            # ADR-0126: a bribe, a threat or a request against someone it is tied to calls for
            # a morale check (once per trigger per person per session), decided by code.
            # Ties: the other parties of relations it is part of or affiliated to (ADR-0119);
            # a public fact everyone knows ("Lehtinan owns the tavern") is not a tie.
            own = {w.lower() for w in req.speaker_name.split()}
            tied = set(known_by_relationship) | {
                e for e in known_now if pack.get(e) is not None
                and pack.get(e).kind == 'RELATIONSHIP'
                and speaker in (pack.get(e).subject_id, pack.get(e).object_id)}
            ties = sorted({w for e in tied for w in re.findall(
                r"[A-ZÀ-Ý][\wÀ-ÿ'-]{2,}", f'{pack.get(e).title} {pack.get(e).summary}')
                if w.lower() not in own})
            trigger = classify_trigger(req.text, ties)
            if trigger is not None:
                check = morale_for(
                    store, view.branch_id, key=memory_key or speaker, session=req.session_seq,
                    trigger=trigger,
                    base=base_morale(role_from_name(req.speaker_name),
                                     curation.morale if curation is not None else None),
                    mods=modifiers(ethical=ethical_axis(getattr(resident, 'alignment', None),
                                                        profile), text=req.text,
                                   trigger=trigger),
                    world_seed=self.args.world_seed, game_time=view.game_time,
                    launch=self.observer.source.launch)
            # SPEC-011: the narrative quests this person is part of move by what the player said;
            # a resolved quest records its milestone before trust is revised.
            story = advance(store, view.branch_id, self.observer.quests, speaker=speaker,
                            text=req.text, area=req.area, game_time=view.game_time,
                            host_epoch=req.session_seq or 0,
                            closed=reaction is not None
                            and reaction.disposition in CLOSED_DISPOSITIONS)
            # ADR-0133: trust by event, after this turn's reaction and morale check are recorded.
            trust = revise_trust(store, view.branch_id, memory_key or speaker,
                                 game_time=view.game_time, host_epoch=req.session_seq or 0,
                                 effects=dict(curation.milestones) if curation else None)
            aliases = local_aliases(pack, req.area)   # "taverna" = the place where it is
            # ADR-0131: titles of what the person does not hold, for the typed-absence check only.
            held_now = set(known_now)
            unheld = tuple(entry.title for entry_id, entry in sorted(pack.entries.items())
                           if entry_id not in held_now)
            result = DialogueEngine(store, self.provider, self.catalog).respond_resident(
                ResidentRequest(speaker, req.speaker_name, req.text, req.area, req.speaker_dead),
                residence_areas=areas, branch_id=view.branch_id, at_game_time=view.game_time,
                profile=profile, identity=identity, also_known=also_known, wisdom=wisdom,
                intelligence=intelligence, game_alignment=getattr(resident, 'alignment', None),
                popular_only_ids=shallow, history=history, recall_lines=lines,
                disposition=reaction.disposition if reaction is not None else None,
                morale=(check.trigger, check.outcome) if check is not None else None,
                unheld_titles=unheld, aliases=aliases, common_words=common_words(pack),
                offer=self.observer.offers.get(speaker),
                trust=trust.level, trust_own_only=trust.own_only,
                quest_facts=story.facts, quest_now=story.fresh,
                order=tuple(context_order(pack, known_now, npc_id=speaker, area=req.area,
                                          home_region=home,
                                          named=named_in(pack, known_now, req.text,
                                                         local_aliases(pack, req.area)))))
            status, reason = result.status.value, result.reason
            flags = list(result.flags)
            speech = result.speech or ('...' if req.speaker_dead else RESIDENT_FALLBACK)
            # ADR-0139/0140: arrival and defeat steps have no conversation; their line goes on the
            # next reply.
            arrived = pending_journal(store, view.branch_id, self.observer.quests)
            # what happened before this turn (arrival, defeat) comes before this turn's own lines
            speech = with_journal(speech, tuple(line for _, _, line in arrived) + story.journal)
            mark_journal_shown(store, view.branch_id, arrived, game_time=view.game_time,
                               host_epoch=req.session_seq or 0)
            used = tuple(e.split(':', 1)[1] for e in result.used_event_ids
                         if e.startswith('canon:'))
            if result.status is DialogueStatus.OK and speaker:
                # The model may name an entry without declaring it: what was said is what was heard.
                used = tuple(dict.fromkeys(used + tuple(entries_named(
                    self.observer.pack, known_now, speech, known_texts, question=question,
                    aliases=aliases))))
            granted = ()
            shareable = tuple(e for e in used if pack.get(e) is not None
                              and pack.get(e).access_scope == 'COMMON_REGIONAL')
            if result.status is DialogueStatus.OK and shareable and req.listeners:
                report = share_knowledge(
                    store, view.branch_id, self.observer.pack, speaker=speaker,
                    listeners=req.listeners, used_entry_ids=shareable, req_id=req.req_id,
                    host_epoch=req.session_seq, at_game_time=view.game_time, speech=speech,
                    also_held=known_by_identity, known_texts=known_texts, question=question,
                    aliases=aliases, speaker_name=req.speaker_name, area=req.area)
                granted = report.granted
                shared = report.status + ''.join(f' {r.entry_id}:{r.reason}' for r in report.refusals
                                                 if r.reason != 'NOT_A_LISTENER')
        turn = self.conversations.add(req.conversation_id, conv_key, req.text, speech)
        if view.branch_id is not None and view.game_time is not None and status != 'DENIED':
            record_turn(store, view.branch_id, key=memory_key, speaker_id=speaker,
                        conversation_id=req.conversation_id, req_id=req.req_id,
                        entries=used if status == 'OK' else (), game_time=view.game_time,
                        host_epoch=req.session_seq)
        with self._lock:
            self._last = {'req_id': req.req_id, 'speaker': req.speaker_name, 'question': req.text,
                          'speech': speech}
        self.writer.put(f'{REPLY_RESREF}.lua', render_reply(req.req_id, speech).encode('utf-8'))
        leader = req.selected_leader
        leader_label = "-"
        if leader is not None:
            leader_chr = leader.charisma_active if leader.charisma_active is not None else "-"
            leader_label = (f'{leader.script_name or leader.display_name}@p{leader.portrait_index}'
                            f':chr={leader_chr}')
        chr_active = req.speaker_charisma_active if req.speaker_charisma_active is not None else "-"
        chr_base = req.speaker_charisma_base if req.speaker_charisma_base is not None else "-"
        morale = (req.speaker_engine_morale_current
                  if req.speaker_engine_morale_current is not None else "-")
        morale_break = (req.speaker_engine_morale_break_active
                        if req.speaker_engine_morale_break_active is not None else "-")
        morale_break_base = (req.speaker_engine_morale_break_base
                             if req.speaker_engine_morale_break_base is not None else "-")
        print(f'{now_iso()} caixa pedido={req.req_id} entrada={req.input} '
              f'falante={speaker or "-"} '
              f'turno={turn or "-"} lembra={earlier.conversations} '
              f'reacao={reaction.summary() if reaction is not None else "-"} '
              f'moral={check.summary() if check is not None else "-"} '
              f'confianca={(trust.level + ("/" + trust.rule if trust.rule else "")) if trust is not None else "-"} '
              f'marcos={list(quests.held) if quests is not None else "-"}'
              f'{" marco_novo=" + str(list(quests.recorded)) if quests and quests.recorded else ""}'
              f'{" marco_regrediu=" + str(list(quests.regressed)) if quests and quests.regressed else ""}'
              f'{" marco_ambiguo=" + str(list(quests.unclear)) if quests and quests.unclear else ""} '
              f'quests={list(story.states) if story is not None else "-"}'
              f'{" quest_mudou=" + str(list(story.changes)) if story and story.changes else ""} '
              f'habitante={bool(areas)} estatuto={standing} perfil={scope} '
              f'identidade={ident_source} '
              f'wis={wisdom or "-"} int={intelligence or "-"} camada={tier} '
              f'chr_ativo={chr_active} chr_base={chr_base} '
              f'morale_engine_atual={morale} morale_break_ativo={morale_break} '
              f'morale_break_base={morale_break_base} selected_leader={leader_label} '
              f'assuntos={len(known_now)} retidos={list(result.withheld)} recusas={flags} '
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
    ap.add_argument('--model', default='qwen3:30b-a3b')
    ap.add_argument('--ollama-url', default='http://127.0.0.1:11434')
    ap.add_argument('--reuse-token', action='store_true',
                    help='keep the token already in --config-out (overlay keeps working after a restart)')
    ap.add_argument('--interval', type=float, default=1.0,
                    help='seconds between observations (reads the shared copy of the log)')
    ap.add_argument('--tail-interval', type=float, default=0.3,
                    help='seconds between reads of the game log (one long-lived shell)')
    ap.add_argument('--language', default='pt_BR', help='game language of the local area inventory')
    ap.add_argument('--campaign-year', type=int, default=1369, help='DR year (ADR-0109)')
    ap.add_argument('--carry-pin', action='store_true',
                    help='CR-2026-020: a branch forked by a loaded save takes the pack revision '
                         'the maintainer already pinned on another branch of this campaign')
    ap.add_argument('--voice', action='store_true',
                    help='push-to-talk in the in-game box (ADR-0127): microphone of this host, '
                         'local STT; off by default')
    ap.add_argument('--stt-model', type=Path,
                    default=Path.home() / '.infinity-ai' / 'models' /
                    'ggml-large-v3-turbo-q5_0.bin', help='whisper.cpp model for --voice')
    ap.add_argument('--mic-device', default=None,
                    help='audio input (index or part of its name); default: the built-in mic')
    ap.add_argument('--max-voice-s', type=float, default=20.0,
                    help='a recording stops by itself after this many seconds')
    ap.add_argument('--min-voice-level', type=float, default=150.0,
                    help='RMS below this is silence (no STT, "não entendi")')
    ap.add_argument('--residence-threshold', type=int, default=DEFAULT_RESIDENCE_THRESHOLD,
                    help='game time an NPC outside the party lives in a region before it knows its '
                         'common knowledge (ADR-0114; party members never learn by time)')
    ap.add_argument('--quest-catalog', type=Path, default=DEFAULT_CATALOG,
                    help='local quest catalog (ADR-0134): allowlisted variables and milestones')
    ap.add_argument('--quest-presence', action='store_true',
                    help='ADR-0138: the quests may create and remove our creatures through the '
                         'action gateway (lab, off by default)')
    ap.add_argument('--local-quests', type=Path, default=None,
                    help='lab only: a folder of test quests kept out of the repository')
    ap.add_argument('--watch-probes', action='store_true',
                    help='print the allowlisted variable values per question (curation, D4)')
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
          f'vendedores: {len(observer.offers)}, '
          f'limite de residencia: {args.residence_threshold}')
    CampaignStore.open(args.db, args.campaign).close()   # migrate once before the threads open it
    # The reply file must exist when the game starts, or Infinity_DoFile never finds it.
    put_override_file(ssh, args.game_root, f'{REPLY_RESREF}.lua', PLACEHOLDER_REPLY.encode('utf-8'))
    # ADR-0127: same for the push-to-talk state (written even without --voice, so the box finds an
    # empty state instead of a missing file).
    put_override_file(ssh, args.game_root, f'{PTT_RESREF}.lua', PLACEHOLDER_PTT.encode('utf-8'))
    # ADR-0134: the variables the box may read, from the local catalog (empty without one). A
    # catalog of another build reads nothing.
    quests = observer.quest_catalog
    allow = [(q.probe_id, q.name) for q in quests.probes] \
        if quests is not None and quests.build_fingerprint == live_build else []
    put_override_file(ssh, args.game_root, f'{QUEST_RESREF}.lua',
                      (render_quest_probes(allow) if allow else PLACEHOLDER_QUEST).encode('utf-8'))
    print(f'quests narrativas: {sorted(observer.quests)}')
    print(f'catalogo de quests: {"nenhum" if quests is None else quests.status + " rev " + quests.revision}'
          f', variaveis permitidas: {len(allow)}')
    # S1i: one long-lived shell reads the log a few times a second, another writes the box files.
    observer.source.refresh()
    LogTail(observer.source, args.tail_interval).start()
    writer = OverrideWriter(ssh, args.game_root)
    observer.start()
    talker = Talker(args, ssh, observer, catalog, writer)
    talker.start()
    if args.quest_presence:              # ADR-0138 D1: off by default
        PresenceDirector(args, ssh, observer, pin_build).start()

    def warm_up() -> None:
        # Load the dialogue model before the first question (a cold load can pass the timeout).
        try:
            OllamaProvider(args.model, base_url=args.ollama_url, timeout_s=300).generate(
                [{'role': 'user', 'content': 'ok'}])
            print(f'{now_iso()} modelo de dialogo carregado')
        except Exception as exc:  # the first question will just be slower
            print(f'{now_iso()} aquecimento do modelo falhou: {type(exc).__name__}')
    threading.Thread(target=warm_up, daemon=True).start()
    if args.voice:
        if not args.stt_model.expanduser().is_file():
            print(f'voz: modelo nao encontrado em {args.stt_model}; voz desligada')
        else:
            VoiceListener(args, ssh, observer, catalog, writer).start()
            print(f'voz ligada: modelo {args.stt_model.name}, limite {args.max_voice_s:g}s')

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
