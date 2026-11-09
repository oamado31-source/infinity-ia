# SPDX-License-Identifier: Apache-2.0
"""P2 adapter tests over synthetic log text (the lab run is the real evidence)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.bridge.domain import (  # noqa: E402
    Allowlist, Audience, Coverage, Evidence, FieldPolicy, Reason, SessionIdentity, Status,
    Visibility,
)
from infinity_ai.bridge.eeex_log import (  # noqa: E402
    ADAPTER_VERSION, AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD, EEexLogAdapter, NoSnapshotError,
    StaleLogError, companion_ids, parse_latest_snapshot, parse_snapshot_line,
)
from infinity_ai.bridge.service import ReadOnlyBridge  # noqa: E402

try:
    import jsonschema
except ImportError:
    jsonschema = None

BUILD, MODPACK = 'sha256:build-lab', 'sha256:modpack-lab'


def probe_line(seq=1, session=0, clock=1000, area='AR0602', time=38974, prefix='INFO: LPRINT: ',
               party=('Imoen',), **extra_fields):
    fields = {AREA_FIELD: area, GAME_TIME_FIELD: time,
              PARTY_FIELD: list(party) if party is not None else None, **extra_fields}
    doc = {'schema': 'infinity-ai.eeex-probe.v1', 'seq': seq, 'session_seq': session,
           'clock_ms': clock, 'fields': fields}
    return f'{prefix}INFAI-P2 {json.dumps(doc)}\n'


class FakeSource:
    def __init__(self, text='', age=1.0):
        self.text, self.age, self.calls = text, age, 0

    def fetch(self):
        self.calls += 1
        return self.text, self.age


class ParserTests(unittest.TestCase):
    def test_parses_probe_line_with_loader_prefix(self):
        snap = parse_snapshot_line(probe_line())
        self.assertEqual((snap.seq, snap.session_seq, snap.clock_ms), (1, 0, 1000))
        self.assertEqual(dict(snap.fields), {AREA_FIELD: 'AR0602', GAME_TIME_FIELD: '38974',
                                             PARTY_FIELD: '["imoen"]'})

    def test_latest_valid_line_wins_and_noise_is_ignored(self):
        text = ('INFO: scanning override\n' + probe_line(seq=1, area='AR0601') +
                'INFO: ERROR! Failed to load file (music)\n' + probe_line(seq=2, area='AR0602') +
                'INFAI-P2 {not json}\n')
        self.assertEqual(parse_latest_snapshot(text).fields[AREA_FIELD], 'AR0602')

    def test_unterminated_last_line_is_skipped(self):
        text = probe_line(seq=1, area='AR0601') + probe_line(seq=2, area='AR0602').rstrip('\n')
        self.assertEqual(parse_latest_snapshot(text).seq, 1)

    def test_glued_line_from_unterminated_print_still_parses(self):
        text = 'INFAI-SPIKE x (EEex_Print)' + probe_line(seq=7)
        self.assertEqual(parse_latest_snapshot(text).seq, 7)

    def test_rejects_malformed_documents(self):
        bad = [
            'INFAI-P2 ' + json.dumps({'schema': 'other', 'seq': 1, 'session_seq': 0,
                                      'clock_ms': 1, 'fields': {}}),
            'INFAI-P2 ' + json.dumps({'schema': 'infinity-ai.eeex-probe.v1', 'seq': -1,
                                      'session_seq': 0, 'clock_ms': 1, 'fields': {}}),
            'INFAI-P2 ' + json.dumps({'schema': 'infinity-ai.eeex-probe.v1', 'seq': True,
                                      'session_seq': 0, 'clock_ms': 1, 'fields': {}}),
            'INFAI-P2 ' + json.dumps({'schema': 'infinity-ai.eeex-probe.v1', 'seq': 1,
                                      'session_seq': 0, 'clock_ms': 1, 'fields': []}),
            'INFAI-P2 ' + 'x' * 5000,
            'INFAI-P2 ',
            'no marker here',
        ]
        for line in bad:
            with self.subTest(line=line[:60]):
                self.assertIsNone(parse_snapshot_line(line))

    def test_only_allowlisted_fields_survive(self):
        snap = parse_snapshot_line(probe_line(**{'quest.hidden_state': 'spoiler',
                                                 'creature.inventory': 'SW1H01'}))
        self.assertEqual(set(snap.fields), {AREA_FIELD, GAME_TIME_FIELD, PARTY_FIELD})
        with self.assertRaises(TypeError):
            snap.fields['quest.hidden_state'] = 'x'

    def test_party_is_normalized_or_unknown_as_a_whole(self):
        cases = {
            ('Imoen', 'Jaheira'): '["imoen","jaheira"]',
            ('Jaheira', 'Imoen', 'Imoen'): '["imoen","jaheira"]',
            (): '[]',
            ('Imoen', 'None'): None,
            ('Imoen', 'bad name'): None,
            ('Imoen', 7): None,
            tuple(f'N{i}' for i in range(6)): None,
        }
        for party, expected in cases.items():
            with self.subTest(party=party):
                self.assertEqual(parse_snapshot_line(probe_line(party=party)).fields[PARTY_FIELD],
                                 expected)
        self.assertIsNone(parse_snapshot_line(probe_line(party=None)).fields[PARTY_FIELD])
        old_probe = probe_line().replace(', "party.companion_ids": ["Imoen"]', '')
        self.assertIsNone(parse_snapshot_line(old_probe).fields[PARTY_FIELD])

    def test_companion_ids_helper(self):
        self.assertEqual(companion_ids('["imoen","jaheira"]'), ('npc:imoen', 'npc:jaheira'))
        self.assertEqual(companion_ids('[]'), ())
        for bad in (None, 'not json', '{"a":1}', '["bad name"]'):
            with self.subTest(bad=bad):
                self.assertIsNone(companion_ids(bad))

    def test_invalid_values_become_none(self):
        cases = [('AR0602"; DROP', 1), ('TOOLONGRESREF', 1), ('', 1), (None, 1), (7, 1),
                 ('AR0602', -5), ('AR0602', '38974'), ('AR0602', True), ('AR0602', 1.5)]
        for area, time in cases:
            with self.subTest(area=area, time=time):
                fields = parse_snapshot_line(probe_line(area=area, time=time)).fields
                if not (isinstance(area, str) and area.isalnum() and len(area) <= 8 and area):
                    self.assertIsNone(fields[AREA_FIELD])
                if not (isinstance(time, int) and not isinstance(time, bool) and time >= 0):
                    self.assertIsNone(fields[GAME_TIME_FIELD])


class AdapterTests(unittest.TestCase):
    def adapter(self, source, **kw):
        return EEexLogAdapter(source, campaign_id='lab', branch_id='main',
                              build_fingerprint=BUILD, modpack_hash=MODPACK, **kw)

    def test_handshake_uses_session_seq_as_epoch(self):
        identity = self.adapter(FakeSource(probe_line(session=3))).handshake()
        self.assertEqual(identity, SessionIdentity('lab', 'main', 3, BUILD, MODPACK,
                                                   ADAPTER_VERSION))

    def test_stale_or_empty_log_fails_closed(self):
        with self.assertRaises(StaleLogError):
            self.adapter(FakeSource(probe_line(), age=11)).handshake()
        with self.assertRaises(StaleLogError):
            self.adapter(FakeSource(probe_line(), age=-1)).read(AREA_FIELD)
        with self.assertRaises(NoSnapshotError):
            self.adapter(FakeSource('INFO: nothing\n')).handshake()

    def test_read_marks_lab_evidence_and_null_as_not_observed(self):
        reading = self.adapter(FakeSource(probe_line())).read(AREA_FIELD)
        self.assertEqual((reading.value, reading.coverage, reading.evidence),
                         ('AR0602', Coverage.FULL, Evidence.LAB_OBSERVED))
        reading = self.adapter(FakeSource(probe_line(area=None, time=None))).read(GAME_TIME_FIELD)
        self.assertEqual((reading.value, reading.coverage), (None, Coverage.NONE))

    def test_unknown_field_reads_nothing(self):
        reading = self.adapter(FakeSource(probe_line())).read('creature.inventory')
        self.assertIsNone(reading.value)


class BridgeIntegrationTests(unittest.TestCase):
    PINNED = SessionIdentity('lab', 'main', 0, BUILD, MODPACK, ADAPTER_VERSION)
    ALLOWLIST = Allowlist(BUILD, (
        FieldPolicy(AREA_FIELD, Visibility.PARTY, frozenset({'narrative_context'})),
        FieldPolicy(GAME_TIME_FIELD, Visibility.PARTY, frozenset({'narrative_context'})),
    ))

    def setUp(self):
        self.source = FakeSource(probe_line(session=0))
        adapter = EEexLogAdapter(self.source, campaign_id='lab', branch_id='main',
                                 build_fingerprint=BUILD, modpack_hash=MODPACK)
        self.bridge = ReadOnlyBridge(self.PINNED, self.ALLOWLIST, adapter,
                                     clock=lambda: '2026-11-08T20:00:00Z',
                                     id_factory=lambda: 'obs', evidence=Evidence.LAB_OBSERVED)

    def ask(self, field, **kw):
        request = {'operation': 'read', 'field': field, 'purpose': 'narrative_context',
                   'audience': 'PLAYER', **kw}
        return self.bridge.handle(request)

    def test_observed_area_and_time(self):
        self.assertTrue(self.bridge.connect().ok)
        area, time = self.ask(AREA_FIELD), self.ask(GAME_TIME_FIELD)
        self.assertEqual((area.status, area.value, area.evidence),
                         (Status.OBSERVED, 'AR0602', Evidence.LAB_OBSERVED))
        self.assertEqual((time.status, time.value), (Status.OBSERVED, '38974'))

    def test_main_menu_is_unknown(self):
        self.source.text = probe_line(area=None, time=None)
        self.bridge.connect()
        env = self.ask(AREA_FIELD)
        self.assertEqual((env.status, env.reason), (Status.UNKNOWN, Reason.NOT_OBSERVED))

    def test_load_changes_epoch_and_closes_session(self):
        self.bridge.connect()
        self.source.text += probe_line(seq=2, session=1, area='AR0700')
        env = self.ask(AREA_FIELD)
        self.assertEqual((env.status, env.reason), (Status.BLOCKED_CAPABILITY,
                                                    Reason.EPOCH_MISMATCH))
        self.assertFalse(self.bridge.session_check.ok)

    def test_game_closed_is_unknown(self):
        self.bridge.connect()
        self.source.age = 60
        env = self.ask(AREA_FIELD)
        self.assertEqual((env.status, env.reason), (Status.UNKNOWN, Reason.ADAPTER_UNAVAILABLE))

    def test_modpack_change_blocks_connect(self):
        adapter = EEexLogAdapter(FakeSource(probe_line()), campaign_id='lab', branch_id='main',
                                 build_fingerprint=BUILD, modpack_hash='sha256:other')
        bridge = ReadOnlyBridge(self.PINNED, self.ALLOWLIST, adapter)
        self.assertEqual(bridge.connect().reasons, (Reason.MODPACK_MISMATCH,))

    def test_adversarial_requests_never_fetch_the_log(self):
        self.bridge.connect()
        before = self.source.calls
        for env in (self.bridge.handle({'operation': 'write', 'field': AREA_FIELD}),
                    self.ask('creature.inventory'), self.ask(AREA_FIELD, purpose='marketing'),
                    self.ask(AREA_FIELD, audience='ADMIN')):
            self.assertNotEqual(env.status, Status.OBSERVED)
            self.assertEqual(env.evidence, Evidence.LAB_OBSERVED)
        self.assertEqual(self.source.calls, before)

    def test_default_context_stays_synthetic(self):
        bridge = ReadOnlyBridge(self.PINNED, self.ALLOWLIST, EEexLogAdapter(
            FakeSource(probe_line()), campaign_id='lab', branch_id='main',
            build_fingerprint=BUILD, modpack_hash=MODPACK))
        self.assertEqual(bridge.handle({'operation': 'write'}).evidence, Evidence.SYNTHETIC)

    @unittest.skipIf(jsonschema is None, 'jsonschema not installed')
    def test_envelopes_match_schema(self):
        schema = json.loads((ROOT / 'src/infinity_ai/bridge/schemas/'
                             'observation_envelope_v1.schema.json').read_text())
        validator = jsonschema.Draft202012Validator(schema)
        self.bridge.connect()
        for env in (self.ask(AREA_FIELD), self.ask(GAME_TIME_FIELD), self.ask('x.y'),
                    self.ask(AREA_FIELD, audience=Audience.HOST.value)):
            validator.validate(env.to_json())


if __name__ == '__main__':
    unittest.main()
