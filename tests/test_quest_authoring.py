# SPDX-License-Identifier: Apache-2.0
"""SPEC-013: the quest checker names every problem; it never disagrees with the loader."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.quests.authoring import (  # noqa: E402
    AuthoringContext, check_quest, rejected_quests,
)
from infinity_ai.quests.narrative import parse_quest  # noqa: E402

QUESTS = ROOT / 'knowledge' / 'quests'
SAREVOK = json.loads((QUESTS / 'sarevok-diary.pt_BR.json').read_text(encoding='utf-8'))
BROOCH = json.loads((QUESTS / 'bernard-brooch.pt_BR.json').read_text(encoding='utf-8'))


def codes(report, kind='errors'):
    return {i.code for i in getattr(report, kind)}


def broken(change):
    doc = copy.deepcopy(SAREVOK)
    change(doc)
    return doc


BAD = {
    'SCHEMA': lambda d: d.update(schema='outro'),
    'CURATION': lambda d: d['curation'].update(status='DRAFT'),
    'MILESTONE': lambda d: d.update(milestone='quest:outra:RESOLVED'),
    'AFTER': lambda d: d['steps'][0].update(after=['descanso']),
    'CHAIN': lambda d: [s.update(after=[]) for s in d['steps'] if s['step_id'] == 'descanso'],
    'GIVER': lambda d: d['steps'][0].update(npc_id=d['giver']['npc_id']),
    'TEXT': lambda d: d['steps'][0].update(fact='x' * 401),
    'CUES': lambda d: d['turn_in'].update(cues=[]),
    'CRE': lambda d: d['presence'][0].update(cre='DRUNK1'),
    'NAME': lambda d: d['presence'][0].update(name='TAMOKO'),
    'WINDOW': lambda d: d['presence'][0].update(until='nao-existe'),
    'COPIES': lambda d: d['presence'][0].update(copies=9),
    'DEFEATED': lambda d: d['presence'].pop(next(i for i, p in enumerate(d['presence'])
                                                 if p['presence_id'] == 'kalessia')),
    'PASSAGE': lambda d: d['passages'][0].update(to='AR0400'),
    'CALL': lambda d: d['call'].update(every=10),
    'STEP_KIND': lambda d: d['steps'][0].update(arrive={'area': 'AR0800'}),
}


class FormatTests(unittest.TestCase):
    def test_the_shipped_quests_pass(self):
        for doc in (SAREVOK, BROOCH):
            report = check_quest(doc)
            self.assertTrue(report.ok, [str(e) for e in report.errors])
            self.assertIsNotNone(parse_quest(doc))

    def test_each_problem_is_named_and_the_loader_agrees(self):
        for code, change in BAD.items():
            with self.subTest(code=code):
                doc = broken(change)
                report = check_quest(doc)
                self.assertIn(code, codes(report))
                self.assertIsNone(parse_quest(doc))     # the loader refuses it too

    def test_never_stricter_than_the_loader(self):
        # dropping any single field: the checker blocks exactly when the loader refuses
        variants = [broken(lambda d, k=k: d.pop(k)) for k in SAREVOK]
        for i, step in enumerate(SAREVOK['steps']):
            variants += [broken(lambda d, i=i, k=k: d['steps'][i].pop(k)) for k in step]
        for i, presence in enumerate(SAREVOK['presence']):
            variants += [broken(lambda d, i=i, k=k: d['presence'][i].pop(k)) for k in presence]
        for doc in variants:
            self.assertEqual(check_quest(doc).ok, parse_quest(doc) is not None,
                             [str(e) for e in check_quest(doc).errors])

    def test_warnings_do_not_block(self):
        doc = broken(lambda d: d['giver'].update(accept_cues=['aceito', 'vou']))
        report = check_quest(doc)
        self.assertTrue(report.ok)
        self.assertIn('ACCEPT_CUES', codes(report, 'warnings'))
        doc = broken(lambda d: d['steps'][0]['cues'].append('que'))
        self.assertIn('COMMON_CUE', codes(check_quest(doc), 'warnings'))
        self.assertNotIn('COMMON_CUE', codes(check_quest(SAREVOK), 'warnings'))   # "sim" to accept


class ContextTests(unittest.TestCase):
    def test_what_does_not_exist_blocks(self):
        people = {SAREVOK['giver']['npc_id']} | {s['npc_id'] for s in SAREVOK['steps']
                                                 if 'npc_id' in s}
        ctx = AuthoringContext(curated=frozenset(people - {'npc:infai_gregor'}),
                               areas=frozenset({'AR0406', 'AR0800', 'AR0409', 'AR0300'}),
                               templates=frozenset({'IATAMOKO', 'IAGREGOR', 'IACARCER',
                                                    'IAKALESS'}))
        report = check_quest(SAREVOK, ctx)
        self.assertIn('NO_CURATION', codes(report))           # Gregor not curated here
        self.assertIn('NO_TEMPLATE', codes(report))           # IAAGENTE not installed here
        self.assertNotIn('AREA', codes(report))               # IA0001 is ours: only a warning
        self.assertIn('OUR_AREA', codes(report, 'warnings'))
        bad_area = broken(lambda d: d['presence'][0].update(area='AR9999'))
        self.assertIn('AREA', codes(check_quest(bad_area, ctx)))

    def test_unknown_names_are_a_warning(self):
        ctx = AuthoringContext(names=frozenset({'Tamoko'}))
        report = check_quest(SAREVOK, ctx)
        self.assertTrue(report.ok)
        self.assertIn('UNKNOWN_NAME', codes(report, 'warnings'))


class ServiceReportTests(unittest.TestCase):
    def test_a_dropped_quest_is_reported_with_its_reasons(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'boa.json').write_text(json.dumps(SAREVOK), encoding='utf-8')
            (Path(tmp) / 'ruim.json').write_text(json.dumps(broken(BAD['CHAIN'])),
                                                 encoding='utf-8')
            (Path(tmp) / 'quebrada.json').write_text('{', encoding='utf-8')
            rejected = rejected_quests(tmp)
        self.assertEqual(set(rejected), {'ruim.json', 'quebrada.json'})
        self.assertTrue(any('[CHAIN]' in r for r in rejected['ruim.json']))


if __name__ == '__main__':
    unittest.main()
