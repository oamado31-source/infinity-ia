# SPDX-License-Identifier: Apache-2.0
"""CR-2026-033: what a quest lets the person say in this line is its subject, and a curated way of
talking (form only) reaches the prompt."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import DialogueContext, Fact, Persona  # noqa: E402
from infinity_ai.dialogue.context import Catalog  # noqa: E402
from infinity_ai.dialogue.engine import DialogueEngine, ResidentRequest, system_prompt  # noqa: E402
from infinity_ai.dialogue.llm import FakeProvider  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402
from infinity_ai.personality.identity import load_curations  # noqa: E402

PERSONA = Persona('npc:drunk1', 'Garoll', ('natural e breve',), frozenset({'Garoll'}))
DRINK = Fact('F1', 'self:npc:drunk1:1', 'Você vive pedindo que paguem uma bebida.', 0)
GHOST = Fact('F2', 'quest:npc:drunk1:1', 'Você viu o fantasma de uma sacerdotisa.', 0)


def context(*facts, speech=None):
    return DialogueContext(PERSONA, facts, frozenset({'Garoll'}), (), resident_of='na Coroa',
                           speech=speech)


class QuestLineTests(unittest.TestCase):
    def test_the_quest_fact_is_marked_and_ruled_first(self):
        prompt = system_prompt(context(DRINK, GHOST))
        self.assertIn('F2: (agora) Você viu o fantasma', prompt)
        self.assertIn('F1: Você vive pedindo', prompt)                  # not marked
        self.assertIn('Um fato marcado (agora) é o assunto desta fala', prompt)
        self.assertLess(prompt.index('F2: (agora)'), prompt.index('F1: Você vive'))  # first

    def test_without_a_quest_fact_nothing_changes(self):
        prompt = system_prompt(context(DRINK))
        self.assertNotIn('(agora)', prompt)
        self.assertNotIn('Seu jeito de falar', prompt)



def said(speech, used=()):
    return json.dumps({'speech': speech, 'used_facts': list(used), 'unknown': False},
                      ensure_ascii=False)


class QuestFactRetryTests(unittest.TestCase):
    """A valid reply that leaves out the fact (agora) is asked once more; the first one stands
    if the second is no better, never the fallback."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)

    def ask(self, provider, now=True):
        return DialogueEngine(self.store, provider, Catalog.load()).respond_resident(
            ResidentRequest('npc:cre-x', 'Campesino(a)', 'Quem é você?', 'AR0406', False),
            residence_areas=(), branch_id=ROOT_BRANCH, at_game_time=10,
            quest_facts=('Você viu um fantasma no cemitério.',),
            quest_now=('Você viu um fantasma no cemitério.',) if now else ())

    def quest_id(self):
        probe = FakeProvider([said('Sou daqui.')] * 2)
        self.ask(probe)
        return re.search(r'(F\d+): \(agora\)', probe.calls[0][0]['content']).group(1)

    def test_a_reply_without_the_quest_fact_is_asked_again(self):
        fid = self.quest_id()
        provider = FakeProvider([said('Sou daqui.'), said('Vi um fantasma no cemitério.', [fid])])
        answer = self.ask(provider)
        self.assertEqual(answer.speech, 'Vi um fantasma no cemitério.')
        self.assertIn('attempt1:QUEST_FACT_MISSING', answer.flags)
        self.assertIn('deixou de fora o fato marcado (agora)', provider.calls[1][-1]['content'])

    def test_a_fact_only_remembered_is_not_forced(self):
        provider = FakeProvider([said('Sou daqui.')])
        answer = self.ask(provider, now=False)
        self.assertEqual(answer.speech, 'Sou daqui.')
        self.assertNotIn('(agora)', provider.calls[0][0]['content'])
        self.assertEqual(len(provider.calls), 1)

    def test_if_the_second_is_no_better_the_first_stands(self):
        provider = FakeProvider([said('Sou daqui.'), said('Moro aqui.')])
        answer = self.ask(provider)
        self.assertEqual((answer.status.value, answer.speech), ('OK', 'Sou daqui.'))

class SpeechTests(unittest.TestCase):
    def test_the_curated_way_of_talking_reaches_the_prompt(self):
        prompt = system_prompt(context(DRINK, speech='bêbado: arrasta as palavras'))
        self.assertIn('Seu jeito de falar: bêbado: arrasta as palavras.', prompt)
        self.assertLess(prompt.index('Seu jeito de falar'), prompt.index('FATOS:'))

    def test_speech_is_optional_short_and_checked(self):
        pack = load_partition(1369)
        base = {'schema': 'infinity-ai.npc-identity-curation.v1', 'language': 'pt_BR',
                'occupation': None, 'origin_region': None, 'self_facts': ['Você bebe.'],
                'curation': {'status': 'CHECKED', 'checked_by': 't', 'checked_at': '2026-11-24'}}
        with tempfile.TemporaryDirectory() as tmp:
            for name, speech in (('ok', 'bêbado'), ('sem', None), ('longo', 'x' * 201),
                                 ('vazio', '  '), ('lista', ['bêbado'])):
                doc = {**base, 'npc_id': f'npc:{name}'}
                if speech is not None:
                    doc['speech'] = speech
                (Path(tmp) / f'{name}.json').write_text(json.dumps(doc), encoding='utf-8')
            curations = load_curations(pack, Path(tmp))
        self.assertEqual(sorted(curations), ['npc:ok', 'npc:sem'])
        self.assertEqual(curations['npc:ok'].speech, 'bêbado')
        self.assertIsNone(curations['npc:sem'].speech)
        garoll = load_curations(pack)['npc:drunk1']
        self.assertTrue(garoll.speech.startswith('bêbado'))


if __name__ == '__main__':
    unittest.main()
