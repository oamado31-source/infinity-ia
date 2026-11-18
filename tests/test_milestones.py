# SPDX-License-Identifier: Apache-2.0
"""ADR-0134: quest milestones from an allowlisted, read-only look at game variables.

Every catalog here is invented (`TesteVar`, `quest:teste:*`): the real catalog, with the game's
variable names, lives only on the lab machine (REQ-CANON-004, ADR-0095 item 6).
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import Catalog as DialogueCatalog  # noqa: E402
from infinity_ai.dialogue.context import build_resident_context  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.personality.identity import load_curations  # noqa: E402
from infinity_ai.personality.morale import MORALE_EVENT  # noqa: E402
from infinity_ai.personality.trust import (  # noqa: E402
    RULE_MILESTONE, assess, revise_trust, trust_of,
)
from infinity_ai.quests.milestones import (  # noqa: E402
    AMBIGUOUS, BLOCKED_BUILD, BLOCKED_MAPPING, MAPPED, MILESTONE_EVENT, NOT_MET, UNKNOWN,
    evaluate, load_catalog, milestones_of, parse_catalog, record_milestones,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

BUILD = 'sha256:build-de-teste'
DONE, KNOWN = 'quest:teste:RESOLVED', 'quest:teste:LEARNED'
DOC = {
    'schema': 'infinity-ai.quest-catalog.v1', 'revision': 'teste-1', 'build_fingerprint': BUILD,
    'status': 'CURATED',
    'probes': [{'probe_id': 'teste-1', 'name': 'TesteVar'},
               {'probe_id': 'teste-2', 'name': 'TesteOutra', 'scope': 'GLOBAL'}],
    'rules': [
        {'semantic_id': KNOWN, 'all': [{'probe_id': 'teste-1', 'op': 'ge', 'values': [1]}]},
        {'semantic_id': DONE, 'all': [{'probe_id': 'teste-1', 'op': 'eq', 'values': [3]},
                                      {'probe_id': 'teste-2', 'op': 'in', 'values': [1, 2]}]},
    ],
}


def statuses(catalog, probes, build=BUILD):
    return {a.semantic_id: a.status for a in evaluate(catalog, probes, build)}


class CatalogTests(unittest.TestCase):
    def test_a_valid_catalog_loads_with_a_digest(self):
        catalog = parse_catalog(DOC)
        self.assertEqual([p.probe_id for p in catalog.probes], ['teste-1', 'teste-2'])
        self.assertTrue(catalog.digest.startswith('sha256:'))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'catalog.json'
            path.write_text(json.dumps(DOC), encoding='utf-8')
            self.assertEqual(load_catalog(path), catalog)
            self.assertIsNone(load_catalog(Path(tmp) / 'missing.json'))

    def test_anything_odd_blocks_the_whole_catalog(self):
        def broken(change):
            doc = copy.deepcopy(DOC)
            change(doc)
            return parse_catalog(doc)
        self.assertIsNone(broken(lambda d: d.update(schema='outro')))
        self.assertIsNone(broken(lambda d: d.update(status='QUASE')))
        self.assertIsNone(broken(lambda d: d['probes'][0].update(scope='AR0406')))   # D3
        self.assertIsNone(broken(lambda d: d['probes'][0].update(name='Teste Var')))
        self.assertIsNone(broken(lambda d: d['probes'].append(dict(d['probes'][0]))))
        self.assertIsNone(broken(lambda d: d['rules'][0]['all'][0].update(probe_id='outro')))
        self.assertIsNone(broken(lambda d: d['rules'][0]['all'][0].update(op='lt')))
        self.assertIsNone(broken(lambda d: d['rules'][0]['all'][0].update(values=[1, 2])))
        self.assertIsNone(broken(lambda d: d['rules'][0]['all'][0].update(values=[True])))
        self.assertIsNone(broken(lambda d: d['rules'][0].update(semantic_id='quest:teste:feito')))
        self.assertIsNone(broken(lambda d: d['rules'].append(dict(d['rules'][0]))))
        self.assertIsNone(broken(lambda d: d.update(probes=[
            {'probe_id': f'p{i}', 'name': f'V{i}'} for i in range(17)])))


class EvaluateTests(unittest.TestCase):
    def setUp(self):
        self.catalog = parse_catalog(DOC)

    def test_predicates(self):
        self.assertEqual(statuses(self.catalog, {'teste-1': 3, 'teste-2': 2}),
                         {KNOWN: MAPPED, DONE: MAPPED})
        self.assertEqual(statuses(self.catalog, {'teste-1': 1, 'teste-2': 2}),
                         {KNOWN: MAPPED, DONE: NOT_MET})
        self.assertEqual(statuses(self.catalog, {'teste-1': 0, 'teste-2': 0}),
                         {KNOWN: NOT_MET, DONE: NOT_MET})

    def test_a_missing_or_absent_variable_is_unknown_never_false(self):
        self.assertEqual(statuses(self.catalog, {'teste-1': 3, 'teste-2': None}),
                         {KNOWN: MAPPED, DONE: UNKNOWN})
        self.assertEqual(statuses(self.catalog, {'teste-1': 3}), {KNOWN: MAPPED, DONE: UNKNOWN})
        self.assertEqual(statuses(self.catalog, None), {KNOWN: UNKNOWN, DONE: UNKNOWN})

    def test_two_exclusive_milestones_together_are_ambiguous(self):
        doc = copy.deepcopy(DOC)
        for rule in doc['rules']:
            rule['exclusive_group'] = 'fim'
        self.assertEqual(statuses(parse_catalog(doc), {'teste-1': 3, 'teste-2': 1}),
                         {KNOWN: AMBIGUOUS, DONE: AMBIGUOUS})

    def test_another_build_or_an_uncurated_catalog_blocks_everything(self):
        reading = {'teste-1': 3, 'teste-2': 1}
        self.assertEqual(set(statuses(self.catalog, reading, 'sha256:outra').values()),
                         {BLOCKED_BUILD})
        pending = parse_catalog({**DOC, 'status': 'REVIEW_PENDING'})
        self.assertEqual(set(statuses(pending, reading).values()), {BLOCKED_MAPPING})
        self.assertEqual(evaluate(None, reading, BUILD), ())


class RecordTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.catalog = parse_catalog(DOC)

    def observe(self, reading, branch=ROOT_BRANCH):
        return record_milestones(self.store, branch, self.catalog,
                                 evaluate(self.catalog, reading, BUILD), game_time=10)

    def test_once_per_branch_without_raw_values(self):
        first = self.observe({'teste-1': 3, 'teste-2': 1})
        self.assertEqual(first.recorded, (KNOWN, DONE))
        again = self.observe({'teste-1': 3, 'teste-2': 1})
        self.assertEqual((again.recorded, again.held), ((), (KNOWN, DONE)))
        events = self.store.visible_events(ROOT_BRANCH, MILESTONE_EVENT)
        self.assertEqual(len(events), 2)
        payload = milestones_of(self.store, ROOT_BRANCH)[DONE].payload
        self.assertEqual(payload['probes'], ['teste-1', 'teste-2'])
        self.assertNotIn('TesteVar', json.dumps(payload))
        self.assertNotIn('3', [str(v) for v in payload.values()])

    def test_a_regression_is_reported_and_never_undone(self):
        self.observe({'teste-1': 3, 'teste-2': 1})
        later = self.observe({'teste-1': 0, 'teste-2': 0})
        self.assertEqual(later.regressed, (KNOWN, DONE))
        self.assertEqual(later.held, (KNOWN, DONE))

    def test_unknown_and_blocked_record_nothing(self):
        self.assertEqual(self.observe(None).held, ())
        pending = parse_catalog({**DOC, 'status': 'REVIEW_PENDING'})
        out = record_milestones(self.store, ROOT_BRANCH, pending,
                                evaluate(pending, {'teste-1': 3, 'teste-2': 1}, BUILD),
                                game_time=10)
        self.assertEqual(out.held, ())


def ev(seq, kind, **payload):
    return SimpleNamespace(seq=seq, event_id=f'e{seq}', event_type=kind, payload=payload)


class TrustTests(unittest.TestCase):
    EFFECTS = {DONE: 'INTIMO'}

    def test_a_milestone_gives_the_curated_level_and_opens_more_than_own_secrets(self):
        trust, cause = assess([ev(1, MILESTONE_EVENT, semantic_id=DONE)], self.EFFECTS)
        self.assertEqual((trust.level, trust.rule, trust.own_only, cause),
                         ('INTIMO', RULE_MILESTONE, False, ('e1',)))
        self.assertEqual(assess([ev(1, MILESTONE_EVENT, semantic_id=KNOWN)],
                                self.EFFECTS)[0].level, 'NEUTRO')
        self.assertEqual(assess([ev(1, MILESTONE_EVENT, semantic_id=DONE)])[0].level, 'NEUTRO')

    def test_the_milestone_takes_a_person_out_of_distrust_and_later_coercion_wins_again(self):
        coerced = ev(1, MORALE_EVENT, npc_key='npc:x', trigger='INTIMIDATION')
        freed = ev(2, MILESTONE_EVENT, semantic_id=DONE)
        self.assertEqual(assess([coerced, freed], self.EFFECTS)[0].level, 'INTIMO')    # D5
        again = ev(3, MORALE_EVENT, npc_key='npc:x', trigger='INTIMIDATION')
        self.assertEqual(assess([coerced, freed, again], self.EFFECTS)[0].level, 'DESCONFIADO')

    def test_revised_from_the_branch_milestone(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CampaignStore.open(Path(tmp) / 'c.sqlite3', 'lab')
            self.addCleanup(store.close)
            catalog = parse_catalog(DOC)
            record_milestones(store, ROOT_BRANCH, catalog,
                              evaluate(catalog, {'teste-1': 3, 'teste-2': 1}, BUILD), game_time=1)
            self.assertEqual(revise_trust(store, ROOT_BRANCH, 'npc:x', game_time=2).level,
                             'NEUTRO')                    # no curated effect: nothing changes
            trust = revise_trust(store, ROOT_BRANCH, 'npc:x', game_time=2, effects=self.EFFECTS)
            self.assertEqual((trust.level, trust.rule), ('INTIMO', RULE_MILESTONE))
            self.assertEqual(trust_of(store, ROOT_BRANCH, 'npc:x'), trust)

    def test_trust_from_a_milestone_opens_the_house_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CampaignStore.open(Path(tmp) / 'c.sqlite3', 'lab')
            self.addCleanup(store.close)
            known = (('rel:house', 'Segredo da Casa', 'A casa esconde algo.', {}, 'RESTRICTED',
                      'npc:y', 'CONFIDENTIAL'),)

            def told(trust, own_only):
                context = build_resident_context(
                    MemoryStore(store), store, DialogueCatalog.load(), npc_id='npc:x',
                    display_name='Teste', residence_areas=('AR0406',), area='AR0406', dead=False,
                    branch_id=ROOT_BRANCH, at_game_time=10, also_known=known, trust=trust,
                    trust_own_only=own_only).context
                return [k.event_id for k in context.restricted_knowledge]
            self.assertEqual(told('CONFIANTE', True), [])          # acquaintance (ADR-0133 D2)
            self.assertEqual(told('INTIMO', False), ['canon:rel:house'])   # milestone


class CurationTests(unittest.TestCase):
    def test_milestone_effects_are_read_and_bad_ones_drop_the_curation(self):
        pack = load_partition(1369)
        base = {'schema': 'infinity-ai.npc-identity-curation.v1', 'language': 'pt_BR',
                'occupation': None, 'origin_region': None, 'years_here': None,
                'places_visited': [], 'self_facts': ['Você é de teste.'],
                'curation': {'status': 'CHECKED', 'checked_by': 't', 'checked_at': '2026-11-17'}}
        with tempfile.TemporaryDirectory() as tmp:
            for name, milestones in (
                    ('ok', [{'milestone': DONE, 'trust': 'INTIMO'}]),
                    ('nivel', [{'milestone': DONE, 'trust': 'NEUTRO'}]),
                    ('id', [{'milestone': 'teste', 'trust': 'INTIMO'}]),
                    ('extra', [{'milestone': DONE, 'trust': 'INTIMO', 'x': 1}]),
                    ('repetido', [{'milestone': DONE, 'trust': 'INTIMO'},
                                  {'milestone': DONE, 'trust': 'DESCONFIADO'}])):
                doc = {**base, 'npc_id': f'npc:{name}', 'milestones': milestones}
                (Path(tmp) / f'{name}.json').write_text(json.dumps(doc), encoding='utf-8')
            curations = load_curations(pack, Path(tmp))
        self.assertEqual(sorted(curations), ['npc:ok'])
        self.assertEqual(curations['npc:ok'].milestones, ((DONE, 'INTIMO'),))

    def test_the_coronet_curations(self):
        curations = load_curations(load_partition(1369))
        freed = 'quest:coronet-slaves:RESOLVED'
        self.assertEqual(dict(curations['npc:hendak'].milestones), {freed: 'INTIMO'})
        for npc in ('npc:lehtinan', 'npc:beast', 'npc:announcer', 'npc:cre-copgreet',
                    'npc:copguard', 'npc:copguard1', 'npc:guard3'):
            self.assertEqual(dict(curations[npc].milestones), {freed: 'DESCONFIADO'}, npc)
        for npc in ('npc:madam', 'npc:escort4'):
            self.assertEqual(curations[npc].milestones, (), npc)
        # SPEC-011: Bernard is moved by his own narrative quest, not by the arena's.
        self.assertEqual(dict(curations['npc:cre-bernard'].milestones),
                         {'quest:bernard-brooch:RESOLVED': 'INTIMO'})


if __name__ == '__main__':
    unittest.main()
