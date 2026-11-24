# SPDX-License-Identifier: Apache-2.0
"""SPEC-011 / ADR-0135: narrative quests carried by the dialogue box (no game writes)."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import Catalog, build_resident_context  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.personality.identity import load_curations  # noqa: E402
from infinity_ai.personality.trust import RULE_MILESTONE, revise_trust  # noqa: E402
from infinity_ai.quests.milestones import MILESTONE_EVENT, milestones_of  # noqa: E402
from infinity_ai.quests.narrative import (  # noqa: E402
    ACCEPTED, OFFERED, QUEST_EVENTS, RESOLVED, STEP_DONE, advance, load_quests, parse_quest,
    says, state_of, with_journal,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

QUEST_FILE = ROOT / 'knowledge' / 'quests' / 'bernard-brooch.pt_BR.json'
DOC = json.loads(QUEST_FILE.read_text(encoding='utf-8'))
BERNARD, YARIN = 'npc:cre-bernard', 'npc:yarin'


class FormatTests(unittest.TestCase):
    def test_the_curated_quest_loads(self):
        quests = load_quests()
        self.assertEqual(sorted(quests), ['bernard-brooch', 'sarevok-diary'])
        quest = quests['bernard-brooch']
        self.assertEqual((quest.giver, [s.npc_id for s in quest.steps], quest.milestone),
                         (BERNARD, [YARIN], 'quest:bernard-brooch:RESOLVED'))

    def test_anything_odd_drops_the_quest(self):
        def broken(change):
            doc = copy.deepcopy(DOC)
            change(doc)
            return parse_quest(doc)
        self.assertIsNotNone(broken(lambda d: None))
        self.assertIsNone(broken(lambda d: d.update(schema='outro')))
        self.assertIsNone(broken(lambda d: d['curation'].update(status='DRAFT')))
        self.assertIsNone(broken(lambda d: d.update(milestone='quest:outra:RESOLVED')))
        self.assertIsNone(broken(lambda d: d['giver'].update(offer_cues=[])))
        self.assertIsNone(broken(lambda d: d['giver'].update(offer_fact='x' * 401)))
        self.assertIsNone(broken(lambda d: d['steps'][0].update(npc_id=BERNARD)))
        self.assertIsNone(broken(lambda d: d['steps'].append(dict(d['steps'][0]))))
        self.assertIsNone(broken(lambda d: d.update(steps=[])))

    def test_cues_are_whole_words_unless_marked_as_a_start(self):
        self.assertTrue(says('Sim, pode contar com a gente.', ('sim',)))
        self.assertFalse(says('Que lugar simpático.', ('sim',)))
        self.assertTrue(says('Quem furtou o broche?', ('furt*',)))
        self.assertTrue(says('Tem TRABALHO pra nós?', ('trabalh*',)))
        self.assertFalse(says('Que trabalho?', ('ajud*',)))


class FlowTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.quests = load_quests()
        self.time = 0

    def say(self, speaker, text, branch=ROOT_BRANCH, area='AR0406'):
        self.time += 10
        return advance(self.store, branch, self.quests, speaker=speaker, text=text, area=area,
                       game_time=self.time)

    def test_the_whole_quest_and_its_milestone(self):
        quest = self.quests['bernard-brooch']
        self.assertEqual(self.say(BERNARD, 'Boa noite, Bernard.').facts, ())
        self.assertEqual(self.say(YARIN, 'Sabe do broche de Bernard?').facts, ())   # not yet
        offer = self.say(BERNARD, 'Você tem algum trabalho para nós?')
        self.assertEqual((offer.facts, offer.changes),
                         ((quest.offer_fact,), (f'bernard-brooch:{OFFERED}',)))
        self.assertEqual(self.say(YARIN, 'Sabe do broche de Bernard?').facts, ())   # REQ-006
        accept = self.say(BERNARD, 'Pode deixar, vamos falar com ele.')
        self.assertEqual(accept.facts, (quest.offer_fact, quest.waiting_fact))
        self.assertEqual(accept.journal, (quest.accept_journal,))
        early = self.say(BERNARD, 'Foi o Yarin?')                 # step not done: still waiting
        self.assertEqual((early.facts, early.changes), ((quest.waiting_fact,), ()))
        self.assertEqual(self.say(YARIN, 'Como vai?').facts, ())  # not about the subject
        step = self.say(YARIN, 'Bernard disse que furtaram o broche dele. Sabe quem foi?')
        self.assertEqual((step.facts, step.journal),
                         ((quest.steps[0].fact,), (quest.steps[0].journal,)))
        self.assertEqual(self.say(YARIN, 'E mais alguma coisa?').facts, (quest.steps[0].fact,))
        done = self.say(BERNARD, 'Yarin disse que foi um novato das Docas.')
        self.assertEqual((done.facts, done.milestones),
                         ((quest.turn_in_fact,), ('quest:bernard-brooch:RESOLVED',)))
        self.assertEqual(done.journal, (quest.turn_in_journal,))
        self.assertEqual(done.states, ('bernard-brooch=RESOLVIDA',))
        event = milestones_of(self.store, ROOT_BRANCH)['quest:bernard-brooch:RESOLVED']
        self.assertEqual((event.payload['source'], event.payload['quest_id']),
                         ('OVERLAY', 'bernard-brooch'))
        later = self.say(BERNARD, 'Alguma novidade do broche?')
        self.assertEqual((later.facts, later.changes), ((quest.turn_in_fact,), ()))
        counts = {t: len(self.store.visible_events(ROOT_BRANCH, t)) for t in QUEST_EVENTS}
        self.assertEqual(counts, {OFFERED: 1, ACCEPTED: 1, STEP_DONE: 1, RESOLVED: 1})
        self.assertEqual(len(self.store.visible_events(ROOT_BRANCH, MILESTONE_EVENT)), 1)
        for t in QUEST_EVENTS:                    # ADR-0107: never the player's text
            for e in self.store.visible_events(ROOT_BRANCH, t):
                self.assertNotIn('Docas', json.dumps(e.payload, ensure_ascii=False))

    def test_another_area_or_another_person_moves_nothing(self):
        self.assertEqual(self.say(BERNARD, 'Tem trabalho?', area='AR0300').changes, ())
        self.assertEqual(self.say('npc:salvanas', 'Tem trabalho?').changes, ())
        self.assertFalse(state_of(self.store, ROOT_BRANCH, 'bernard-brooch').offered)

    def test_a_closed_person_moves_no_quest_and_tells_nothing(self):
        out = advance(self.store, ROOT_BRANCH, self.quests, speaker=BERNARD,
                      text='Tem trabalho?', area='AR0406', game_time=5, closed=True)
        self.assertEqual((out.facts, out.changes, out.states), ((), (), ('bernard-brooch=NOVA',)))
        self.assertFalse(state_of(self.store, ROOT_BRANCH, 'bernard-brooch').offered)

    def test_an_older_save_has_the_quest_where_it_was(self):
        self.say(BERNARD, 'Tem trabalho?')                       # t=10
        self.say(BERNARD, 'Aceito.')                             # t=20
        older = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=15,
                                       fork_epoch=1)
        state = state_of(self.store, older, 'bernard-brooch')
        self.assertEqual((state.offered, state.accepted), (True, False))
        self.assertEqual(self.say(YARIN, 'Quem roubou o broche?', branch=older).facts, ())

    def test_the_journal_line_goes_after_the_reply(self):
        self.assertEqual(with_journal('Obrigado.', ('Tarefa concluída.',)),
                         'Obrigado. (Diário: Tarefa concluída.)')
        self.assertEqual(with_journal('Obrigado.', ()), 'Obrigado.')


class TrustTests(unittest.TestCase):
    def test_the_quest_makes_bernard_intimate_and_he_may_tell_the_house_secret(self):
        pack = load_partition(1369)
        effects = dict(load_curations(pack)[BERNARD].milestones)
        self.assertEqual(effects, {'quest:bernard-brooch:RESOLVED': 'INTIMO'})
        with tempfile.TemporaryDirectory() as tmp:
            store = CampaignStore.open(Path(tmp) / 'c.sqlite3', 'lab')
            self.addCleanup(store.close)
            quests = load_quests()
            for i, (who, text) in enumerate((
                    (BERNARD, 'Tem trabalho?'), (BERNARD, 'Combinado.'),
                    (YARIN, 'Quem furtou o broche de Bernard?'),
                    (BERNARD, 'Yarin falou de um novato nas Docas.')), 1):
                advance(store, ROOT_BRANCH, quests, speaker=who, text=text, area='AR0406',
                        game_time=i)
            trust = revise_trust(store, ROOT_BRANCH, BERNARD, game_time=9, effects=effects)
            self.assertEqual((trust.level, trust.rule, trust.own_only),
                             ('INTIMO', RULE_MILESTONE, False))
            entry = pack.get('rel:arena-slaves')
            known = (('rel:arena-slaves', entry.title, entry.summary, entry.layers or {},
                      entry.access_scope, entry.subject_id, entry.secrecy),)

            def told(level, own_only):
                context = build_resident_context(
                    MemoryStore(store), store, Catalog.load(), npc_id=BERNARD,
                    display_name='Bernard', residence_areas=('AR0406',), area='AR0406',
                    dead=False, branch_id=ROOT_BRANCH, at_game_time=10, also_known=known,
                    trust=level, trust_own_only=own_only,
                    quest_facts=(quests['bernard-brooch'].turn_in_fact,)).context
                return context
            neutral, intimate = told('NEUTRO', False), told(trust.level, trust.own_only)
            self.assertEqual(neutral.restricted_knowledge, ())
            self.assertEqual([k.event_id for k in intimate.restricted_knowledge],
                             ['canon:rel:arena-slaves'])
            self.assertIn(quests['bernard-brooch'].turn_in_fact,
                          [f.text for f in intimate.facts])


class BatteryTests(unittest.TestCase):
    def test_battery_cases_use_the_curated_texts(self):
        quest = load_quests()['bernard-brooch']
        cases = {c['id']: c for c in json.loads(
            (ROOT / 'tests' / 'dialogue_eval' / 'cases.pt_BR.json').read_text())['cases']}
        self.assertEqual(cases['bernard-oferece-o-broche']['speaker']['quest_facts'],
                         [quest.offer_fact])
        self.assertEqual(cases['yarin-conta-do-batedor']['speaker']['quest_facts'],
                         [quest.steps[0].fact])
        self.assertEqual(cases['bernard-intimo-conta-dos-escravos']['speaker']['quest_facts'],
                         [quest.turn_in_fact])


if __name__ == '__main__':
    unittest.main()
