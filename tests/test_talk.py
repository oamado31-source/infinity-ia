# SPDX-License-Identifier: Apache-2.0
"""In-game dialogue box: protocol parsing, reply escaping and static checks on the Lua module."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.bridge.manifest import modpack_hash  # noqa: E402
from infinity_ai.bridge.talk import (  # noqa: E402
    PLACEHOLDER_PTT, PLACEHOLDER_REPLY, TALK_SCHEMA, fresh_ptt_signals, lua_string,
    parse_ptt_signals,
    parse_talk_line, parse_talk_requests, render_ptt_state, render_reply,
)
from types import SimpleNamespace  # noqa: E402

from infinity_ai.personality.in_game import (  # noqa: E402
    profile_for, record_dialogue_start, resolve_speaker,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402
from test_eeex_probe import FORBIDDEN, strip_lua  # noqa: E402

try:
    import lupa  # type: ignore
except ImportError:  # optional, like in test_eeex_probe
    lupa = None

MODULE = ROOT / 'tools' / 'eeex-probe' / 'M_INFAIT.lua'
MENU = ROOT / 'tools' / 'eeex-probe' / 'INFAITLK.menu'
ALLOWED = frozenset({
    'EEex_Sprite_GetInPortrait', 'EEex_GameObject_GetUnderCursor', 'EEex_Sprite_GetName',
    'EEex_Area_GetVisible', 'EEex_Area_GetAllOfTypeStringInRange',
    'EEex_Menu_AddMainFileLoadedListener', 'EEex_Menu_LoadFile', 'EEex_Key_AddPressedListener',
    'EEex_Key_GetFromName', 'EEex_Key_GetName', 'EEex_GameState_AddDestroyedListener',
    'Infinity_GetScreenSize',
    'Infinity_SetArea', 'Infinity_PushMenu', 'Infinity_PopMenu', 'Infinity_FocusTextEdit',
    'Infinity_TextEditHasFocus', 'Infinity_GetClockTicks', 'Infinity_DoFile',
    'EEex_Resource_Fetch', 'EEex_GameState_TogglePause', 'EEex_Key_Hook_AfterEventsPoll',
    'EEex_Sprite_GetActiveStats',  # read-only: active creature stats
    'EEex_Sprite_GetSelectedID',  # read-only: selected group leader ID (EEex 1.1.0+, ADR-0122)
})


def line(**over):
    doc = {'schema': TALK_SCHEMA, 'req_id': '1-2500-1', 'session_seq': 1, 'clock_ms': 2500,
           'area': 'AR0406', 'game_time': 53322, 'input': 'TEXT',
           'speaker': {'script': 'Bernard', 'name': 'Bernard', 'cre': 'bernar', 'instance': 7,
                       'dead': False},
           'text': 'Quem governa Amn?', 'listeners': ['Jaheira', 'Imoen']}
    doc.update(over)
    return 'INFO: LPRINT: INFAI-TALK ' + json.dumps(doc, ensure_ascii=False) + '\n'


class ParseTests(unittest.TestCase):
    def test_valid_request(self):
        req = parse_talk_line(line())
        self.assertEqual(req.req_id, '1-2500-1')
        self.assertEqual(req.speaker_id, 'npc:bernard')
        self.assertEqual(req.listeners, ('npc:imoen', 'npc:jaheira'))
        self.assertEqual((req.area, req.game_time, req.input), ('AR0406', 53322, 'TEXT'))
        self.assertEqual(req.speaker_instance, 7)
        self.assertFalse(req.speaker_party)
        companion = parse_talk_line(line(speaker={'script': 'Jaheira', 'name': 'Jaheira',
                                                  'cre': 'jaheira', 'dead': False,
                                                  'party': True}))
        self.assertTrue(companion.speaker_party)
        self.assertEqual(companion.speaker_id, 'npc:jaheira')
        self.assertEqual((req.speaker_wisdom, req.speaker_intelligence), (None, None))
        scored = parse_talk_line(line(speaker={'script': 'Minsc', 'name': 'Minsc', 'cre': 'minsc',
                                               'dead': False, 'party': True, 'wis': 6, 'int': 8}))
        self.assertEqual((scored.speaker_wisdom, scored.speaker_intelligence), (6, 8))
        odd = parse_talk_line(line(speaker={'script': 'Minsc', 'name': 'Minsc', 'cre': 'minsc',
                                            'dead': False, 'wis': 0, 'int': 99}))
        self.assertEqual((odd.speaker_wisdom, odd.speaker_intelligence), (None, None))
        self.assertIsNone(req.conversation_id)                       # old box: no conversation
        conv = parse_talk_line(line(conv='0-123456'))
        self.assertEqual(conv.conversation_id, '0-123456')
        self.assertIsNone(parse_talk_line(line(conv='abc; drop')).conversation_id)

    def test_social_stats_and_selected_leader_are_observations_only(self):
        req = parse_talk_line(line(
            speaker={'script': 'Bernard', 'name': 'Bernard', 'cre': 'bernar', 'instance': 7,
                     'dead': False, 'chr_active': 16, 'chr_base': 15,
                     'engine_morale_current': 12, 'engine_morale_break_active': 5,
                     'engine_morale_break_base': 6},
            selected_leader={'script': 'CHARNAME', 'name': 'Charname', 'instance': 1,
                             'portrait': 0, 'chr_active': 18, 'chr_base': 18},
        ))
        self.assertEqual((req.speaker_charisma_active, req.speaker_charisma_base), (16, 15))
        self.assertEqual((req.speaker_engine_morale_current,
                          req.speaker_engine_morale_break_active,
                          req.speaker_engine_morale_break_base), (12, 5, 6))
        self.assertEqual(req.selected_leader.script_name, 'CHARNAME')
        self.assertEqual(req.selected_leader.portrait_index, 0)
        self.assertEqual((req.selected_leader.charisma_active,
                          req.selected_leader.charisma_base), (18, 18))

    def test_unavailable_or_out_of_range_social_values_remain_unknown(self):
        req = parse_talk_line(line(
            speaker={'script': 'Bernard', 'name': 'Bernard', 'cre': 'bernar',
                     'dead': False, 'chr_active': 26, 'engine_morale_current': 21,
                     'engine_morale_break_active': -1},
            selected_leader={'script': 'CHARNAME', 'name': 'Charname', 'instance': 1,
                             'portrait': 6, 'chr_active': 18, 'chr_base': 18},
        ))
        self.assertIsNotNone(req)
        self.assertIsNone(req.speaker_charisma_active)
        self.assertIsNone(req.speaker_engine_morale_current)
        self.assertIsNone(req.speaker_engine_morale_break_active)
        self.assertIsNone(req.selected_leader)

    def test_speaker_without_script_and_unreadable_listeners(self):
        req = parse_talk_line(line(speaker={'script': '', 'name': 'Plebeu', 'cre': 'common',
                                            'dead': False}, listeners=None))
        self.assertEqual(req.speaker_id, 'npc:cre-common')
        nobody = parse_talk_line(line(speaker={'script': '', 'name': 'x', 'cre': '../x',
                                               'dead': False}))
        self.assertIsNone(nobody.speaker_id)
        self.assertIsNone(req.listeners)

    def test_malformed_lines_are_dropped(self):
        bad = [line(schema='x'), line(req_id='1; os.exit()'), line(text=''), line(text='a' * 501),
               line(input='COMMAND'), line(listeners=['A', 'B', 'C', 'D', 'E', 'F']),
               line(listeners=['None']), line(speaker={'script': 'a b', 'name': 'x', 'dead': False}),
               line(speaker={'script': 'x', 'name': 'x', 'dead': 'no'}), line(session_seq=-1),
               'INFAI-TALK {not json}\n', 'INFAI-P2 {}\n']
        for raw in bad:
            with self.subTest(raw=raw[:60]):
                self.assertIsNone(parse_talk_line(raw))

    def test_bad_area_is_unknown_not_fatal(self):
        self.assertIsNone(parse_talk_line(line(area='../../x')).area)

    def test_requests_in_order_and_partial_last_line_skipped(self):
        text = line() + 'noise\n' + line(req_id='1-2600-2') + line(req_id='1-2700-3').rstrip('\n')
        self.assertEqual([r.req_id for r in parse_talk_requests(text)], ['1-2500-1', '1-2600-2'])


class DialogueStartTests(unittest.TestCase):
    """The box request as SPEC-006's trusted dialogue-start observation."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def req(self, req_id='1-2500-1', script='', cre='bernar', instance=7, dead=False):
        return parse_talk_line(line(req_id=req_id, speaker={
            'script': script, 'name': 'Bernard', 'cre': cre, 'instance': instance, 'dead': dead}))

    def start(self, req, t=100):
        event = record_dialogue_start(self.store, ROOT_BRANCH, req, game_time=t)
        return event, profile_for(self.store, ROOT_BRANCH, event, at_game_time=t,
                                  world_seed='lab-seed')[:2]

    def test_generic_person_gets_a_temporary_profile_stable_per_instance(self):
        (event, (profile, scope)) = self.start(self.req())
        self.assertEqual(scope, 'ENCOUNTER')
        self.assertEqual(len(profile['hexaco']), 6)
        self.assertNotIn('text', event.payload)
        self.assertEqual(event.payload['identity_state'], 'CANDIDATE')
        _, (again, _) = self.start(self.req(req_id='1-2600-2'), t=110)
        _, (other, _) = self.start(self.req(req_id='1-2700-3', instance=8), t=120)
        self.assertEqual(again, profile)                    # same person in the same scene
        self.assertNotEqual(other, profile)                 # another person
        self.assertEqual(self.store.visible_events(ROOT_BRANCH, 'NpcPersonalityAssigned'), [])

    def test_script_named_creature_is_canonical_and_not_randomized(self):
        _, (profile, scope) = self.start(self.req(script='Rumar', cre='rumar'))
        self.assertIsNone(profile)
        self.assertEqual(scope, 'CANONICAL')

    def test_dead_or_unplaced_speaker_gets_no_profile(self):
        _, (profile, scope) = self.start(self.req(dead=True))
        self.assertIsNone(profile)
        self.assertTrue(scope.startswith('NO_PROFILE'))

    def test_saved_game_cre_star_is_matched_in_the_area(self):
        def res(npc, cre, script='', areas=('AR0406',)):
            return SimpleNamespace(npc_id=npc, cre_resref=cre, script_name=script, areas=areas)
        residents = {'npc:cre-bernard': res('npc:cre-bernard', 'BERNARD'),
                     'npc:cre-xernard': res('npc:cre-xernard', 'XERNARD', areas=('AR0300',)),
                     'npc:rumar': res('npc:rumar', 'RUMAR', script='Rumar')}
        star = self.req(cre='*ERNARD')
        self.assertIsNone(star.speaker_id)
        self.assertEqual(resolve_speaker(star, residents), 'npc:cre-bernard')
        self.assertIsNone(resolve_speaker(self.req(cre='*UMAR'), residents))  # has a script
        self.assertEqual(resolve_speaker(self.req(script='Rumar', cre='*UMAR'), residents),
                         'npc:rumar')
        residents['npc:cre-zernard'] = res('npc:cre-zernard', 'ZERNARD')
        self.assertIsNone(resolve_speaker(star, residents))                  # ambiguous
        event = record_dialogue_start(self.store, ROOT_BRANCH, star, game_time=1,
                                      speaker_id='npc:cre-bernard')
        self.assertEqual(event.payload['speaker_id'], 'npc:cre-bernard')

    def test_one_event_per_request(self):
        first, _ = self.start(self.req())
        second, _ = self.start(self.req())
        self.assertEqual(first.event_id, second.event_id)


class ReplyTests(unittest.TestCase):
    def test_lua_string_has_no_raw_breakers(self):
        literal = lua_string('a"b\\c\nd\x7f]]--')
        self.assertTrue(literal.startswith('"') and literal.endswith('"'))
        self.assertNotRegex(literal[1:-1], r'(?<!\\)"|[\n\r\x00-\x1f\x7f]')
        self.assertIn('\\034', literal)

    def test_render_reply_shape(self):
        out = render_reply('1-2500-1', 'O  Conselho\n dos Seis.')
        self.assertEqual(out, 'INFAI_TALK_Reply = {req_id = "1-2500-1", '
                              'speech = "O Conselho dos Seis."}\n')
        with self.assertRaises(ValueError):
            render_reply('1"} os.exit() --', 'x')

    def test_reply_file_does_not_change_the_modpack(self):
        def manifest(*files):
            return {'game': {'override_files': [{'path': p, 'sha256': h * 64} for p, h in files],
                             'weidu_log_sha256': None, 'eeex_markers': [],
                             'mod_setup_markers': []}}
        base = manifest(('override/M_INFAIT.lua', 'a'))
        self.assertEqual(modpack_hash(base), modpack_hash(manifest(
            ('override/M_INFAIT.lua', 'a'), ('override/INFAIRSP.lua', 'b'))))
        self.assertEqual(modpack_hash(base), modpack_hash(manifest(        # ADR-0127
            ('override/M_INFAIT.lua', 'a'), ('override/INFAIPTT.lua', 'c'))))
        self.assertNotEqual(modpack_hash(base), modpack_hash(manifest(
            ('override/M_INFAIT.lua', 'a'), ('override/OTHER.lua', 'b'))))

    @unittest.skipIf(lupa is None, 'lupa not installed')
    def test_placeholder_defines_an_empty_reply(self):
        lua = lupa.LuaRuntime()
        lua.execute(PLACEHOLDER_REPLY)
        self.assertEqual(lua.globals().INFAI_TALK_Reply['req_id'], '')

    @unittest.skipIf(lupa is None, 'lupa not installed')
    def test_reply_round_trips_and_cannot_inject(self):
        speech = 'Fim"} INFAI_PWNED = true --\nçãé \\ \x01 ]] [[x'
        lua = lupa.LuaRuntime()
        lua.execute(render_reply('1-2500-1', speech))
        reply = lua.globals().INFAI_TALK_Reply
        self.assertEqual(reply['speech'], ' '.join(speech.split()))
        self.assertIsNone(lua.globals().INFAI_PWNED)


class PushToTalkProtocolTests(unittest.TestCase):
    """ADR-0127: INFAI-PTT signals from the box and the INFAIPTT.lua state file."""

    def line(self, **over):
        doc = {'schema': 'infinity-ai.ptt.v1', 'ptt_id': '1-2500-3', 'action': 'START',
               'session_seq': 1, 'clock_ms': 2500, **over}
        return 'INFAI-PTT ' + json.dumps(doc) + '\n'

    def test_signals_are_parsed_strictly(self):
        (s,) = parse_ptt_signals(self.line() + 'other\n' + self.line(action='STOP')[:-1])
        self.assertEqual((s.ptt_id, s.action, s.session_seq), ('1-2500-3', 'START', 1))
        for bad in (self.line(action='RECORD'), self.line(schema='x'), self.line(ptt_id='1"x'),
                    self.line(session_seq=-1), 'INFAI-PTT {not json}\n'):
            with self.subTest(bad=bad):
                self.assertEqual(parse_ptt_signals(bad), [])

    def test_only_fresh_presses_of_this_session_open_the_microphone(self):
        """S1h: a restarted service replayed old presses and opened the mic by itself."""
        old = parse_ptt_signals(self.line(ptt_id='0-1000-1', clock_ms=1000) +
                                self.line(ptt_id='0-1000-1', action='STOP', clock_ms=3000))
        seen: set = set()
        # Latest snapshot at 60 s: the presses from 1-3 s are stale, and are marked seen.
        self.assertEqual(fresh_ptt_signals(old, seen, session_seq=1, clock_ms=60_000), [])
        self.assertEqual(fresh_ptt_signals(old, seen, session_seq=1, clock_ms=2_000), [])
        new = parse_ptt_signals(self.line(ptt_id='1-59000-2', clock_ms=59_000))
        self.assertEqual([s.ptt_id for s in fresh_ptt_signals(new, seen, session_seq=1,
                                                              clock_ms=55_000)], ['1-59000-2'])
        other = parse_ptt_signals(self.line(ptt_id='0-59000-3', clock_ms=59_000, session_seq=0))
        self.assertEqual(fresh_ptt_signals(other, set(), session_seq=1, clock_ms=59_000), [])

    def test_state_file(self):
        self.assertEqual(render_ptt_state('1-2500-3', 'REC', 'ignored'),
                         'INFAI_PTT_State = {ptt_id = "1-2500-3", state = "REC", text = ""}\n')
        out = render_ptt_state('1-2500-3', 'TEXT', 'Quem\n governa  "Amn"?')
        self.assertIn('text = "Quem governa \\034Amn\\034?"', out)
        for args in (('1"} x', 'REC'), ('1-2-3', 'PLAY')):
            with self.subTest(args=args), self.assertRaises(ValueError):
                render_ptt_state(*args)

    @unittest.skipIf(lupa is None, 'lupa not installed')
    def test_state_file_cannot_inject(self):
        lua = lupa.LuaRuntime()
        lua.execute(PLACEHOLDER_PTT)
        self.assertEqual(lua.globals().INFAI_PTT_State['state'], '')
        lua.execute(render_ptt_state('1-2-3', 'TEXT', 'x"} INFAI_PWNED = true --'))
        self.assertIsNone(lua.globals().INFAI_PWNED)


@unittest.skipIf(lupa is None, 'lupa not installed')
class PushToTalkBoxTests(unittest.TestCase):
    """The box module itself, run with a stubbed engine: press, record, stop, review, send."""

    STUBS = """
    printed = {}
    print = function(s) table.insert(printed, s) end
    clock = 1000
    files = {}
    Infinity_GetClockTicks = function() return clock end
    Infinity_DoFile = function(name) local f = files[name]; if f then load(f)() end end
    Infinity_FocusTextEdit = function() end
    Infinity_PushMenu = function() end
    Infinity_PopMenu = function() end
    Infinity_GetScreenSize = function() return 1280, 720 end
    Infinity_SetArea = function() end
    EEex_Resource_Fetch = function() return nil end
    EEex_Menu_AddMainFileLoadedListener = function() end
    EEex_Key_AddPressedListener = function() end
    EEex_GameState_AddDestroyedListener = function() end
    EEex_GameState_TogglePause = function() end
    EEex_Key_Hook_AfterEventsPoll = function() return false end
    worldScreen = { CheckIfPaused = function() return true end }
    """

    def setUp(self):
        self.lua = lupa.LuaRuntime()
        self.lua.execute(self.STUBS)
        self.lua.execute(MODULE.read_text(encoding='utf-8'))
        self.g = self.lua.globals()
        self.lua.execute("""
        INFAI_TALK_State.open = true
        INFAI_TALK_State.speaker = { id = 7, script = "", name = "Bernard", cre = "BERNARD",
                                     dead = false, party = false, wis = 10, int = 10, x = 0, y = 0 }
        INFAI_TALK_State.lines = {}
        """)

    def tick(self, ms=600):
        self.g.clock = self.g.clock + ms
        self.g.INFAI_TALK_Tick()

    def printed(self):
        return [self.g.printed[i] for i in range(1, len(self.g.printed) + 1)]

    def serve(self, state, text=''):
        ptt_id = self.g.INFAI_TALK_State.ptt.id
        self.g.files['INFAIPTT'] = render_ptt_state(ptt_id, state, text)

    def test_press_record_stop_review_and_send_as_voice(self):
        self.g.INFAI_TALK_PTT()
        (start,) = parse_ptt_signals('\n'.join(self.printed()) + '\n')
        self.assertEqual(start.action, 'START')
        self.assertEqual(self.g.INFAI_TALK_PTTText(), 'Preparando o microfone...')
        self.serve('REC')
        self.tick()
        self.assertEqual(self.g.INFAI_TALK_PTTText(), 'Gravando... clique para parar')
        self.g.INFAI_TALK_PTT()
        self.assertEqual(parse_ptt_signals('\n'.join(self.printed()) + '\n')[-1].action, 'STOP')
        self.assertEqual(self.g.INFAI_TALK_PTTText(), 'Transcrevendo...')
        self.serve('TEXT', 'Quem governa Amn?')
        self.tick()
        self.assertEqual(self.g.INFAI_TALK_Input, 'Quem governa Amn?')
        self.assertIsNone(self.g.INFAI_TALK_State.ptt)
        self.g.INFAI_TALK_Send()
        (req,) = parse_talk_requests('\n'.join(self.printed()) + '\n')
        self.assertEqual((req.input, req.text), ('VOICE', 'Quem governa Amn?'))

    def test_failure_close_and_timeout(self):
        self.g.INFAI_TALK_PTT()
        self.serve('FAILED')
        self.tick()
        self.assertIsNone(self.g.INFAI_TALK_State.ptt)
        self.assertIn('Não entendi', self.g.INFAI_TALK_State.lines[1])
        self.g.INFAI_TALK_PTT()                                      # no answer at all
        self.tick(11000)
        self.assertIsNone(self.g.INFAI_TALK_State.ptt)
        self.assertIn('microfone não respondeu', self.g.INFAI_TALK_State.lines[2])
        self.g.INFAI_TALK_PTT()
        self.g.INFAI_TALK_Close()
        self.assertEqual(parse_ptt_signals('\n'.join(self.printed()) + '\n')[-1].action, 'CANCEL')
        self.g.INFAI_TALK_State.open = True
        self.g.INFAI_TALK_Input = 'typed'
        self.g.INFAI_TALK_Send()
        self.assertEqual(parse_talk_requests('\n'.join(self.printed()) + '\n')[-1].input, 'TEXT')


class ModuleStaticTests(unittest.TestCase):
    def setUp(self):
        self.raw = MODULE.read_text(encoding='utf-8')
        self.code = strip_lua(self.raw)

    def test_only_allowlisted_engine_functions(self):
        used = set(re.findall(r'\b(?:EEex|Infinity)_\w+', self.code))
        self.assertEqual(used - ALLOWED, set())

    def test_no_forbidden_capabilities(self):
        self.assertIsNone(FORBIDDEN.search(self.code), FORBIDDEN.search(self.code))

    def test_companions_open_the_box_but_not_the_protagonist(self):
        self.assertIn('member.portrait == 0 then return nil', self.raw)
        self.assertIn('party = member ~= nil', self.raw)
        self.assertIn(''',"party":''', self.raw)

    def test_box_sends_a_conversation_id_per_opening(self):
        self.assertIn('st.conv = string.format("%d-%d"', self.raw)
        self.assertIn(''',"conv":''', self.raw)

    def test_box_sends_the_speaker_ability_scores(self):
        self.assertIn('EEex_Sprite_GetActiveStats(object).m_nWIS', self.raw)
        self.assertIn('EEex_Sprite_GetActiveStats(object).m_nINT', self.raw)
        self.assertIn('EEex_Sprite_GetActiveStats(object).m_nCHR', self.raw)
        self.assertIn('object.m_baseStats.m_CHRBase', self.raw)
        self.assertIn('object.m_baseStats.m_morale', self.raw)
        self.assertIn('EEex_Sprite_GetActiveStats(object).m_nMoraleBreak', self.raw)
        self.assertIn('object.m_baseStats.m_moraleBreak', self.raw)
        self.assertIn(''',"wis":''', self.raw)
        self.assertIn(''',"int":''', self.raw)
        self.assertIn(''',"chr_active":''', self.raw)
        self.assertIn(''',"engine_morale_current":''', self.raw)

    def test_box_captures_selected_leader_as_candidate_not_proven_initiator(self):
        self.assertIn('EEex_Sprite_GetSelectedID()', self.raw)
        self.assertIn('local member = infai_party_ids()[id]', self.raw)
        self.assertIn('if member == nil then return nil', self.raw)
        self.assertIn('local selected_leader = infai_selected_leader()', self.raw)
        self.assertIn('selected_leader_json', self.raw)

    def test_right_click_hook_wraps_and_delegates(self):
        self.assertIn('local infai_events_poll = EEex_Key_Hook_AfterEventsPoll', self.raw)
        self.assertIn('return infai_events_poll(event)', self.raw)
        self.assertIn('event.button.button ~= 3', self.raw)

    def test_pause_only_undoes_its_own_pause(self):
        self.assertEqual(self.code.count('EEex_GameState_TogglePause'), 2)
        self.assertIn('st.paused_by_box', self.raw)

    def test_only_the_service_files_are_dropped_from_cache(self):
        # ADR-0127: the reply and the push-to-talk state, behind an explicit guard.
        self.assertEqual(re.findall(r'EEex_Resource_Fetch\(([^)]*)\)', self.raw), ['resref, "LUA"'])
        self.assertIn('if resref ~= "INFAIRSP" and resref ~= "INFAIPTT" then return false', self.raw)
        self.assertEqual(sorted(re.findall(r'infai_drop_cached\("(\w+)"\)', self.raw)),
                         ['INFAIPTT', 'INFAIRSP'])
        self.assertEqual(self.code.count('EngineGlobals.'), 1)
        self.assertIn('EngineGlobals.dimmDump(res)', self.raw)

    def test_reads_only_the_service_files(self):
        self.assertEqual(self.code.count('Infinity_DoFile'), 2)
        rest = self.raw.replace('pcall(Infinity_DoFile, "INFAIRSP")', '').replace(
            'pcall(Infinity_DoFile, "INFAIPTT")', '')
        self.assertEqual(strip_lua(rest).count('Infinity_DoFile'), 0)

    def test_push_to_talk_signals_and_marks_voice_input(self):
        """ADR-0127: the box only signals; it never records audio itself."""
        self.assertIn('"INFAI-PTT {"', self.raw)
        for action in ('"START"', '"STOP"', '"CANCEL"'):
            self.assertIn(f'infai_ptt_signal({action})', self.raw)
        self.assertIn('st.from_voice and "VOICE" or "TEXT"', self.raw)
        self.assertIn('INFAI_TALK_Input = s.text', self.raw)
        self.assertNotRegex(self.code, r'(?i)microphone|record_audio|capture')

    def test_never_assigns_to_engine_state(self):
        for src_line in self.code.splitlines():
            for lhs in re.findall(r'([\w.\[\]:]+)\s*=(?!=)', src_line):
                if src_line.strip().startswith(('if ', 'elseif ')):
                    continue
                with self.subTest(line=src_line.strip()):
                    self.assertNotRegex(lhs, r'\.m_|:|EngineGlobals')
                    root = lhs.split('.')[0].split('[')[0]
                    self.assertTrue(root.startswith(('INFAI_', 'infai_')) or root.islower(), lhs)

    def test_menu_is_bound_to_the_module(self):
        menu = MENU.read_text(encoding='utf-8')
        for name in ('INFAI_TALK_Menu', 'INFAI_TALK_Edit', 'INFAI_TALK_PTT', 'INFAI_TALK_Tick()',
                     'INFAI_TALK_Send()', 'INFAI_TALK_Close()', 'INFAI_TALK_Input',
                     'INFAI_TALK_PTT()', 'INFAI_TALK_PTTText()'):
            self.assertIn(name, menu)
        self.assertIn('"INFAITLK"', self.raw)


if __name__ == '__main__':
    unittest.main()
