# SPDX-License-Identifier: Apache-2.0
"""ADR-0117 NPC identity: game data, curation, deterministic background and dialogue use."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.canon.pack import load_partition  # noqa: E402
from infinity_ai.dialogue.context import (  # noqa: E402
    Catalog, DialogueContext, Fact, Persona, build_resident_context,
)
from infinity_ai.dialogue.engine import (  # noqa: E402
    DialogueEngine, DialogueStatus, ResidentRequest, system_prompt,
)
from infinity_ai.dialogue.llm import FakeProvider  # noqa: E402
from infinity_ai.dialogue.validate import validate_reply  # noqa: E402
from infinity_ai.canon.pin import pin_pack  # noqa: E402
from infinity_ai.memory.common_knowledge import (  # noqa: E402
    conveyed, entries_named, heard, identity_entries, identity_knowledge, local_aliases,
    share_knowledge,
)
from infinity_ai.personality.style import orientation_from_game_alignment  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.personality.identity import (  # noqa: E402
    CURATED, CURATION_SCHEMA, GAME_DATA, GENERATED, build_identity, em, generate_identity,
    knowledge_tier, layered_text, load_curations, role_from_name,
)
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore  # noqa: E402

PACK = load_partition(1369)
REGION_TITLES = {e.title for e in PACK.entries.values() if e.kind == 'REGION'}


def gen(npc='npc:generated:enc-1', role='COMMONER', home='region:athkatla', **kw):
    args = dict(npc_id=npc, role=role, gender=1, home_region=home, pack=PACK, world_seed='w',
                campaign_id='lab', branch_id=ROOT_BRANCH)
    args.update(kw)
    return generate_identity(**args)


def resident(**kw):
    base = dict(gender=1, race=1, klass=0, display_name='Bernard')
    base.update(kw)
    return SimpleNamespace(**base)


class RoleAndPlaceTests(unittest.TestCase):
    def test_role_words_in_game_names(self):
        self.assertEqual(role_from_name('Guarda da Coroa de Cobre'), 'GUARD')
        self.assertEqual(role_from_name('Cliente da Taverna'), 'PATRON')
        self.assertEqual(role_from_name('Campesino(a)'), 'COMMONER')
        self.assertEqual(role_from_name('Leão de Chácara'), 'GUARD')
        self.assertIsNone(role_from_name('Bernard'))

    def test_portuguese_contraction(self):
        self.assertEqual(em('a Coroa de Cobre'), 'na Coroa de Cobre')
        self.assertEqual(em('o Porto'), 'no Porto')
        self.assertEqual(em('Athkatla'), 'em Athkatla')


class KnowledgeTierTests(unittest.TestCase):
    COUNCIL = PACK.get('org:council-of-six')

    def text(self, wis, int_=10):
        return layered_text(self.COUNCIL.summary, self.COUNCIL.layers, knowledge_tier(wis, int_))

    def test_tiers_by_wisdom(self):
        self.assertEqual([knowledge_tier(w).level for w in (3, 6, 7, 10, 11, 14, 15, 17, 18, 25)],
                         [1, 1, 2, 2, 3, 3, 4, 4, 5, 5])
        self.assertEqual(knowledge_tier(None).level, 2)                      # unknown = 10
        self.assertEqual(knowledge_tier(0).name, 'comum')

    def test_layers_grow_with_wisdom(self):
        popular, informed = self.COUNCIL.layers['POPULAR'], self.COUNCIL.layers['INFORMED']
        self.assertEqual(self.text(5), popular)
        self.assertEqual(self.text(9), popular)
        self.assertEqual(self.text(12), f'{popular} {informed}')
        self.assertNotIn('Meisarch', self.text(14))
        self.assertIn('Meisarch', self.text(16))                          # perspicaz: partial

    def test_intelligence_unlocks_studied_knowledge(self):
        self.assertEqual(knowledge_tier(9, 10).studied, 'NONE')
        self.assertEqual(knowledge_tier(9, 14).studied, 'PARTIAL')          # studious, average WIS
        self.assertEqual(knowledge_tier(9, 18).studied, 'FULL')
        self.assertEqual(knowledge_tier(18, 12).studied, 'FULL')
        self.assertEqual(knowledge_tier(18, 8).studied, 'NONE')             # wise but unlettered
        self.assertFalse(knowledge_tier(9, 14).informed)                 # INT does not grant INFORMED
        self.assertIn('Meisarch', self.text(9, 14))                     # INT grants STUDIED partial
        self.assertNotIn('tortura', self.text(9, 14))                   # INFORMED remains locked

    def test_intelligence_can_unlock_studied_without_wisdom_or_informed(self):
        tier = knowledge_tier(5, 17)
        self.assertEqual(tier.level, 1)
        self.assertFalse(tier.informed)
        self.assertEqual(tier.studied, 'FULL')
        popular = self.COUNCIL.layers['POPULAR']
        studied = self.COUNCIL.layers['STUDIED']
        self.assertEqual(layered_text(self.COUNCIL.summary, self.COUNCIL.layers, tier),
                         f'{popular} {studied}')
        self.assertNotIn('tortura', layered_text(self.COUNCIL.summary, self.COUNCIL.layers, tier))
        self.assertEqual(layered_text(self.COUNCIL.summary, self.COUNCIL.layers,
                                      knowledge_tier(5, 10)), popular)

    def test_entry_without_layers_splits_the_summary(self):
        tier = knowledge_tier(9)
        self.assertEqual(layered_text('Um. Dois. Três.', None, tier), 'Um.')
        self.assertEqual(layered_text('Um. Dois. Três.', None, knowledge_tier(12)), 'Um. Dois. Três.')

    def test_shipped_layers_restate_only_summary_names(self):
        for entry in PACK.entries.values():
            if not entry.layers:
                continue
            names = {w for t in entry.layers.values() for w in re.findall(r'\b[A-ZÀ-Ý]\w+', t)}
            allowed = set(re.findall(r'\b[A-ZÀ-Ý]\w+', entry.summary + ' ' + entry.title)) | {
                'É', 'Por', 'Depois', 'Fica', 'Foram', 'Usam', 'Reúnem', 'Restringem', 'Tem',
                'Governam', 'Reino', 'Terra', 'Magos', 'Isso', 'Essa', 'Amn', 'Athkatla', 'Tethyr',
                'Conselho', 'Seis', 'DR', 'A', 'O', 'Os', 'As'}
            with self.subTest(entry=entry.id):
                self.assertTrue(names <= allowed, names - allowed)


class GeneratorTests(unittest.TestCase):
    def test_deterministic_and_only_pack_regions(self):
        self.assertEqual(gen(), gen())
        self.assertNotEqual(gen(), gen(npc='npc:generated:enc-2'))
        regions = {e.id for e in PACK.entries.values() if e.kind == 'REGION'}
        for i in range(40):
            g = gen(npc=f'npc:generated:enc-{i}')
            self.assertIn(g['origin_region'], regions)
            self.assertTrue(set(g['places_visited']) <= regions)
            self.assertLessEqual(len(g['places_visited']), 2)
            if g['born_here'] or g['standing'] != 'HABITANTE':
                self.assertIsNone(g['years_here'])
            else:
                self.assertTrue(1 <= g['years_here'] <= 40)

    def test_occupation_only_from_the_closed_vocabulary(self):
        self.assertIsNone(gen(role='GUARD')['occupation'])        # the game name says it
        self.assertIn(gen(role=None)['occupation'],                # no role: an ordinary trade
                      {'carregador', 'lavrador', 'artesão', 'pescador', 'ajudante de ferreiro'})
        self.assertIn(gen(role='PATRON', gender=2)['occupation'],
                      {'carregadora do porto', 'artesã', 'mercadora de passagem', 'mercenária',
                       'escriturária'})


class BuildTests(unittest.TestCase):
    def test_game_data_only_for_an_official_npc(self):
        ident = build_identity(npc_id='npc:rumar', name='Rumar', pack=PACK,
                               place='a Coroa de Cobre', home_region='region:athkatla',
                               resident=resident(display_name='Rumar', klass=4))
        self.assertEqual(ident.source, GAME_DATA)
        self.assertIn('Você vive em Athkatla e está na Coroa de Cobre.', ident.self_facts)
        self.assertIn('Você é humano.', ident.self_facts)
        self.assertIn('Você tem treino de ladrão.', ident.self_facts)
        self.assertFalse(any('veio de' in f or 'passou por' in f for f in ident.self_facts))

    def test_unknown_curated_origin_does_not_fall_back_to_generated_history(self):
        cur = SimpleNamespace(occupation='taverneiro da Coroa de Cobre', origin_region=None,
                              years_here=None, places_visited=(),
                              self_facts=('Você serve bebida no balcão.',))
        ident = build_identity(npc_id='npc:cre-bernard', name='Bernard', pack=PACK,
                               place='a Coroa de Cobre', home_region='region:athkatla',
                               resident=resident(), curation=cur, generated=gen())
        self.assertIsNone(ident.origin_region)
        self.assertNotIn('origin', ident.provenance)
        self.assertFalse(any('veio de' in f or 'passou por' in f for f in ident.self_facts))
        self.assertIn('Você vive em Athkatla e está na Coroa de Cobre.', ident.self_facts)

    def test_generated_background_names_only_pack_regions(self):
        ident = build_identity(npc_id='npc:cre-ftown7', name='Cliente da Taverna', pack=PACK,
                               place='a Coroa de Cobre', home_region='region:athkatla',
                               resident=resident(gender=2, display_name='Cliente da Taverna'),
                               generated=gen(role='PATRON', gender=2))
        self.assertEqual(ident.source, GENERATED)
        names = {w for f in ident.self_facts for w in re.findall(r'\b[A-ZÀ-Ý]\w+', f)}
        allowed = {'Você', 'Cliente', 'Taverna', 'Coroa', 'Cobre'} | \
            {w for t in REGION_TITLES for w in t.split()}
        self.assertTrue(names <= allowed, names - allowed)

    def test_curation_wins_over_game_data_and_generation(self):
        cur = SimpleNamespace(occupation='taverneiro da Coroa de Cobre', origin_region='region:tethyr',
                              years_here=12, places_visited=(), self_facts=('Você serve bebida.',))
        ident = build_identity(npc_id='npc:cre-bernard', name='Bernard', pack=PACK,
                               place='a Coroa de Cobre', home_region='region:athkatla',
                               resident=resident(), curation=cur, generated=gen())
        self.assertEqual(ident.occupation, 'taverneiro da Coroa de Cobre')
        self.assertIn('Você veio de Tethyr e vive aqui há 12 anos.', ident.self_facts)
        self.assertEqual(ident.provenance['occupation'], CURATED)
        self.assertEqual(ident.source, CURATED)


class CurationFileTests(unittest.TestCase):
    def write(self, folder, **over):
        doc = {'schema': CURATION_SCHEMA, 'npc_id': 'npc:cre-bernard', 'occupation': 'taverneiro',
               'origin_region': None, 'places_visited': [], 'self_facts': ['Você serve bebida.'],
               'curation': {'checked_by': 'mantenedor', 'checked_at': '2026-11-10'}}
        doc.update(over)
        (Path(folder) / 'bernard.json').write_text(json.dumps(doc), encoding='utf-8')

    def test_unchecked_or_unknown_regions_are_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d)
            self.assertIn('npc:cre-bernard', load_curations(PACK, Path(d)))
            for over in ({'curation': {'checked_by': '', 'checked_at': ''}},
                         {'origin_region': 'region:rashemen'}, {'schema': 'x'}):
                self.write(d, **over)
                self.assertEqual(load_curations(PACK, Path(d)), {})

    def test_shipped_curation_is_checked_and_short(self):
        doc = json.loads((ROOT / 'knowledge' / 'npcs' / 'bernard.pt_BR.json').read_text('utf-8'))
        self.assertEqual(doc['schema'], CURATION_SCHEMA)
        self.assertTrue(all(len(f) <= 200 for f in doc['self_facts']))
        curation = load_curations(PACK)['npc:cre-bernard']
        self.assertEqual(curation.occupation, 'taverneiro da Coroa de Cobre')
        self.assertEqual(curation.origin_region, 'region:tethyr')
        self.assertEqual(curation.affiliations, ('place:copper-coronet:STAFF',))


BUILD = frozenset(a for e in PACK.entries.values() for a in e.area_resrefs)


class HomelandAndHomeTests(unittest.TestCase):
    def test_homeland_and_home_common_knowledge(self):
        known = identity_entries(PACK, homeland='region:tethyr', home='region:athkatla',
                                 campaign_year=1369, build_areas=BUILD)
        self.assertEqual(set(known), {'region:tethyr', 'event:tethyr-reclamation-wars-end',
                                      'region:athkatla', 'region:amn', 'org:council-of-six',
                                      'org:cowled-wizards', 'place:copper-coronet',
                                      'rel:lehtinan-owns-copper-coronet'})
        self.assertNotIn('org:shadow-thieves', known)                      # not common
        countryside = identity_entries(PACK, homeland=None, home='region:amn',
                                       campaign_year=1369, build_areas=BUILD)
        self.assertEqual(set(countryside), {'region:amn', 'org:cowled-wizards'})
        self.assertEqual(identity_entries(PACK, homeland='region:rashemen', home=None,
                                          campaign_year=1369, build_areas=BUILD), [])

    def test_listeners_learn_the_homeland_from_what_is_said(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(store.close)
        store.append_event(branch_id=ROOT_BRANCH, host_epoch=0, event_type='PartyChanged',
                           category='CAMPAIGN_OBSERVATION', game_time=1,
                           payload={'members': ['npc:jaheira'], 'previous': None},
                           evidence='SYNTHETIC', idempotency_key='p1')
        pin_pack(store, ROOT_BRANCH, PACK, game_time=1)
        report = share_knowledge(
            store, ROOT_BRANCH, PACK, speaker='npc:cre-bernard', listeners=['npc:jaheira'],
            used_entry_ids=['region:tethyr'], req_id='1-2-3', host_epoch=0, at_game_time=5,
            speech='Tethyr, minha terra, saiu há pouco de anos de guerra.',
            also_held=['region:tethyr'])
        self.assertEqual(report.status, 'OK')
        self.assertIn('region:tethyr', MemoryStore(store).known_canon('npc:jaheira', ROOT_BRANCH))


class ConveyedTests(unittest.TestCase):
    """Naming a subject is not telling it (lab S1e: "Sou de Athkatla" taught Athkatla)."""
    ATHKATLA, COUNCIL = PACK.get('region:athkatla'), PACK.get('org:council-of-six')

    def test_name_alone_does_not_teach(self):
        said = 'Sou de Athkatla. Estou aqui porque a cidade me pertence.'
        self.assertFalse(conveyed(self.ATHKATLA, self.ATHKATLA.layers['POPULAR'], said,
                                  question='De onde você é? E o que faz aqui?'))
        self.assertEqual(entries_named(PACK, ['region:athkatla'], said,
                                       {'region:athkatla': self.ATHKATLA.layers['POPULAR']}), [])

    def test_content_or_the_question_context_teaches(self):
        self.assertTrue(conveyed(self.COUNCIL, self.COUNCIL.layers['POPULAR'],
                                 'Conselho dos Seis. Ninguém sabe quem são.'))
        self.assertTrue(conveyed(self.COUNCIL, self.COUNCIL.layers['POPULAR'],
                                 'O Conselho dos Seis.', question='Quem governa Amn?'))
        self.assertFalse(conveyed(self.COUNCIL, self.COUNCIL.layers['POPULAR'],
                                  'O Conselho dos Seis.', question='Conhece algum grupo?'))


class GameAlignmentTests(unittest.TestCase):
    def test_official_alignment_becomes_orientation(self):
        self.assertEqual(orientation_from_game_alignment(0x13),
                         'valoriza regras e compromissos; costuma priorizar seus próprios interesses')
        self.assertIsNone(orientation_from_game_alignment(0))
        self.assertIsNone(orientation_from_game_alignment(None))


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.calls = []

    def factory(self, npc_id):
        self.calls.append(npc_id)
        return gen(npc=npc_id)

    def event(self, kind, payload, t, category='CAMPAIGN_OBSERVATION'):
        return self.store.append_event(branch_id=ROOT_BRANCH, host_epoch=0, event_type=kind,
                                       category=category, game_time=t, payload=payload,
                                       evidence='SYNTHETIC', idempotency_key=f'{kind}-{t}')[0]

    def contact(self, t, **extra):
        doc = {'dialogue_started': True, 'target_visible': True, 'access_allowed': True,
               'session_id': 's', 'scene_id': 'AR0406', 'actor_instance_token': 'a1',
               'token_uniqueness': 'SCENE_VERIFIED', 'role': 'OTHER',
               'identity_state': 'CANDIDATE'}
        doc.update(extra)
        return self.event('NpcDialogueStarted', doc, t)

    def begin(self, event, t):
        from infinity_ai.personality import FirstContactService
        return FirstContactService(self.store, world_seed='w').begin(
            contact_event_id=event.event_id, branch_id=ROOT_BRANCH, at_game_time=t,
            identity_factory=self.factory)

    def test_encounter_identity_is_stable_and_not_stored(self):
        a, b = self.begin(self.contact(10), 10), self.begin(self.contact(11), 11)
        self.assertEqual(a.identity, b.identity)
        self.assertEqual(self.store.visible_events(ROOT_BRANCH, 'NpcPersonalityAssigned'), [])

    def test_canonical_gets_no_generated_background(self):
        contact = self.begin(self.contact(10, identity_state='CANONICAL'), 10)
        self.assertIsNone(contact.identity)
        self.assertEqual(self.calls, [])

    def test_verified_identity_is_stored_once_and_reused(self):
        npc = 'npc:generated:beggar-1'
        proof = self.event('NpcIdentityVerified', {
            'identity_state': 'VERIFIED', 'npc_id': npc, 'session_id': 's', 'scene_id': 'AR0406',
            'actor_instance_token': 'a1'}, 5, category='CAMPAIGN_FACT')
        first = self.begin(self.contact(10, identity_state='VERIFIED', verified_npc_id=npc,
                                         identity_proof_event_id=proof.event_id), 10)
        again = self.begin(self.contact(20, identity_state='VERIFIED', verified_npc_id=npc,
                                         identity_proof_event_id=proof.event_id), 20)
        self.assertEqual(first.identity, again.identity)
        self.assertEqual(self.calls, [npc])              # generated once, then read back
        stored = self.store.visible_events(ROOT_BRANCH, 'NpcPersonalityAssigned')[0]
        self.assertEqual(stored.payload['identity'], first.identity)


class DialogueTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.ident = build_identity(npc_id='npc:cre-ftown7', name='Cliente da Taverna',
                                    pack=PACK, place='a Coroa de Cobre',
                                    home_region='region:athkatla',
                                    resident=resident(display_name='Cliente da Taverna'),
                                    generated={**gen(role='PATRON'), 'standing': 'HABITANTE'})

    def ctx(self):
        return build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:cre-ftown7',
            display_name='Cliente da Taverna', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, identity=self.ident).context

    def test_identity_becomes_facts_about_oneself(self):
        context = self.ctx()
        self.assertEqual([f.text for f in context.facts], list(self.ident.self_facts))
        prompt = system_prompt(context)
        self.assertIn('F2: Você vive em Athkatla e está na Coroa de Cobre.', prompt)
        self.assertIn('8. Sobre você mesmo(a)', prompt)
        self.assertIn(self.ident.occupation, prompt)

    def test_answer_about_oneself_cites_identity_facts(self):
        reply = json.dumps({'speech': 'Moro aqui na Coroa de Cobre, em Athkatla.',
                            'used_facts': ['F2'], 'unknown': False}, ensure_ascii=False)
        result = DialogueEngine(self.store, FakeProvider([reply]), Catalog.load()).respond_resident(
            ResidentRequest('npc:cre-ftown7', 'Cliente da Taverna', 'Onde você mora?', 'AR0406',
                            False), residence_areas=(), branch_id=ROOT_BRANCH, at_game_time=10,
            identity=self.ident)
        self.assertEqual(result.status, DialogueStatus.OK)
        self.assertEqual(result.used_event_ids, ('identity:npc:cre-ftown7:2',))

    def test_homeland_knowledge_reaches_the_prompt(self):
        tethyr = PACK.get('region:tethyr')
        context = build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:cre-ftown7',
            display_name='Cliente da Taverna', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, identity=self.ident,
            also_known=(('region:tethyr', tethyr.title, tethyr.summary, tethyr.layers),)).context
        self.assertEqual([k.event_id for k in context.knowledge], ['canon:region:tethyr'])
        self.assertIn('K1: Tethyr:', system_prompt(context))

    def test_public_relationship_reaches_resident_dialogue(self):
        relation = PACK.get('rel:lehtinan-owns-copper-coronet')
        known = ((relation.id, relation.title, relation.summary, relation.layers),)
        raw = json.dumps({'speech': 'Lehtinan é o dono da Coroa de Cobre.',
                          'used_facts': ['K1'], 'unknown': False}, ensure_ascii=False)
        result = DialogueEngine(self.store, FakeProvider([raw]), Catalog.load()).respond_resident(
            ResidentRequest('npc:cre-bernard', 'Bernard', 'Quem é o dono da Coroa de Cobre?',
                            'AR0406', False), residence_areas=('AR0406',),
            branch_id=ROOT_BRANCH, at_game_time=10, also_known=known)
        self.assertEqual(result.status, DialogueStatus.OK, result.flags)
        self.assertEqual(result.used_event_ids, ('canon:rel:lehtinan-owns-copper-coronet',))

    def test_restricted_relationship_reaches_its_own_prompt_section(self):
        relation = PACK.get('rel:bernard-manages-copper-coronet')
        known = ((relation.id, relation.title, relation.summary, relation.layers,
                  relation.access_scope, relation.subject_id),)
        raw = json.dumps({'speech': 'Bernard cuida do atendimento e da operação cotidiana da Coroa de Cobre em nome de Lehtinan.',
                          'used_facts': ['K1'], 'unknown': False}, ensure_ascii=False)
        result = DialogueEngine(self.store, FakeProvider([raw]), Catalog.load()).respond_resident(
            ResidentRequest('npc:cre-bernard', 'Bernard', 'Quem cuida da operação da Coroa de Cobre?',
                            'AR0406', False), residence_areas=('AR0406',),
            branch_id=ROOT_BRANCH, at_game_time=10, also_known=known)
        self.assertEqual(result.status, DialogueStatus.OK, result.flags)
        self.assertEqual(result.used_event_ids, ('canon:rel:bernard-manages-copper-coronet',))

    def test_self_claims_outside_the_facts_are_refused(self):
        bad = json.dumps({'speech': 'Estou aqui porque a cidade me pertence.', 'used_facts': [],
                          'unknown': False}, ensure_ascii=False)
        result = DialogueEngine(self.store, FakeProvider([bad, bad]), Catalog.load()
                                ).respond_resident(
            ResidentRequest('npc:cre-ftown7', 'Cliente da Taverna', 'O que faz aqui?', 'AR0406',
                            False), residence_areas=(), branch_id=ROOT_BRANCH, at_game_time=10,
            identity=self.ident)
        self.assertEqual(result.status, DialogueStatus.FALLBACK)
        self.assertTrue(any('SELF_CLAIM' in f for f in result.flags))

    def test_true_title_from_the_own_name_is_not_a_false_claim(self):
        ok = json.dumps({'speech': 'Sou o Lorde Jierdan, e isso basta.', 'used_facts': [],
                         'unknown': False}, ensure_ascii=False)
        result = DialogueEngine(self.store, FakeProvider([ok]), Catalog.load()).respond_resident(
            ResidentRequest('npc:firkra01', 'Lorde Jierdan', 'Quem é você?', 'AR0406', False),
            residence_areas=(), branch_id=ROOT_BRANCH, at_game_time=10)
        self.assertEqual(result.status, DialogueStatus.OK, result.flags)

    def test_public_fact_about_oneself_can_be_claimed(self):
        owner = PACK.get('rel:lehtinan-owns-copper-coronet')
        self.assertIsNotNone(owner)
        also = ((owner.id, owner.title, owner.summary, owner.layers, owner.access_scope,
                 owner.subject_id),)
        context = build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:lehtinan',
            display_name='Lehtinan', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, also_known=also).context
        k = context.knowledge[0]
        self.assertIn(f'{k.fact_id}: (sobre você)', system_prompt(context))
        reply = json.dumps({'speech': 'Sim, eu sou o dono desta casa.', 'used_facts': [k.fact_id],
                            'unknown': False}, ensure_ascii=False)
        result = DialogueEngine(self.store, FakeProvider([reply]), Catalog.load()
                                ).respond_resident(
            ResidentRequest('npc:lehtinan', 'Lehtinan', 'Você é o dono?', 'AR0406', False),
            residence_areas=(), branch_id=ROOT_BRANCH, at_game_time=10, also_known=also)
        self.assertEqual(result.status, DialogueStatus.OK, result.flags)

    def test_official_npc_speaks_with_its_game_alignment(self):
        context = build_resident_context(
            MemoryStore(self.store), self.store, Catalog.load(), npc_id='npc:lehtinan',
            display_name='Lehtinan', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, game_alignment=0x13).context
        self.assertIn('Orientação: valoriza regras', system_prompt(context))

    def test_prompt_asks_for_own_words(self):
        prompt = system_prompt(self.ctx())
        self.assertIn('sem copiar a frase do texto', prompt)
        # Rules 2, 7 and 8 carry out-of-world examples again (S1f: copied facts, recited lists).
        self.assertIn('"O rio enche na primavera"', prompt)
        self.assertIn('não recite a lista de FATOS', prompt)
        self.assertIn('"Isso não é da sua conta."', prompt)
        self.assertIn('"Tesouro? Não faço ideia', prompt)

    def test_invented_unknown_place_is_refused(self):
        bad = json.dumps({'speech': 'Eu vim de Waterdeep, sou só um viajante.', 'used_facts': [],
                          'unknown': False}, ensure_ascii=False)
        result = DialogueEngine(self.store, FakeProvider([bad, bad]), Catalog.load()
                                ).respond_resident(
            ResidentRequest('npc:cre-ftown7', 'Cliente da Taverna', 'De onde você é?', 'AR0406',
                            False), residence_areas=(), branch_id=ROOT_BRANCH, at_game_time=10,
            identity=self.ident)
        self.assertEqual(result.status, DialogueStatus.FALLBACK)
        self.assertTrue(any('UNKNOWN_NAMES:Waterdeep' in f for f in result.flags))


if __name__ == '__main__':
    unittest.main()


class StandingTests(unittest.TestCase):
    """ADR-0120: resident, traveler (same realm, passing through) and outsider (distant land)."""

    def test_standing_is_drawn_by_role_and_deterministic(self):
        self.assertEqual(gen(role='TRAVELER'), gen(role='TRAVELER'))
        for i in range(30):
            npc = f'npc:generated:enc-{i}'
            self.assertNotEqual(gen(npc=npc, role='TRAVELER')['standing'], 'HABITANTE')
            self.assertEqual(gen(npc=npc, role='GUARD')['standing'], 'HABITANTE')
        patrons = {gen(npc=f'npc:generated:enc-{i}', role='PATRON')['standing'] for i in range(60)}
        self.assertEqual(patrons, {'HABITANTE', 'VIAJANTE', 'FORASTEIRO'})

    def test_residents_keep_their_previous_draws(self):
        # The standing has its own seed: a resident's trade and origin did not change.
        for i in range(30):
            g = gen(npc=f'npc:generated:enc-{i}', role='PATRON')
            if g['standing'] == 'HABITANTE':
                self.assertTrue(g['born_here'] or 1 <= g['years_here'] <= 40)

    def test_origin_matches_the_standing(self):
        for i in range(60):
            g = gen(npc=f'npc:generated:enc-{i}', role='TRAVELER')
            if g['standing'] == 'VIAJANTE':
                self.assertEqual(g['origin_region'], 'region:amn')          # same realm
            else:
                self.assertEqual(g['origin_region'], 'region:tethyr')       # distant land
            self.assertIsNone(g['years_here'])
            self.assertFalse(g['born_here'])

    def test_facts_follow_the_standing(self):
        def facts(standing, origin):
            g = {**gen(role='PATRON'), 'standing': standing, 'origin_region': origin,
                 'born_here': False, 'years_here': None}
            return build_identity(npc_id='npc:cre-x', name='Cliente da Taverna', pack=PACK,
                                  place='a Coroa de Cobre', home_region='region:athkatla',
                                  resident=resident(), generated=g)
        traveler = facts('VIAJANTE', 'region:amn')
        self.assertIn('Você está de passagem por Athkatla e está agora na Coroa de Cobre.',
                      traveler.self_facts)
        self.assertIn('Você veio de Amn.', traveler.self_facts)
        self.assertEqual(traveler.standing, 'VIAJANTE')
        outsider = facts('FORASTEIRO', 'region:tethyr')
        self.assertTrue(any(f.startswith('Você é de Tethyr, terra distante')
                            for f in outsider.self_facts))
        self.assertEqual(facts('HABITANTE', 'region:athkatla').standing, 'HABITANTE')

    def test_curated_standing_wins_and_must_be_known(self):
        curation = SimpleNamespace(occupation='nobre de Athkatla', origin_region=None,
                                   years_here=None, places_visited=(), self_facts=(),
                                   affiliations=(), standing='HABITANTE')
        ident = build_identity(npc_id='npc:firkra01', name='Lorde Jierdan', pack=PACK,
                               place='a Coroa de Cobre', home_region='region:athkatla',
                               curation=curation,
                               generated={**gen(role='TRAVELER')})
        self.assertEqual((ident.standing, ident.provenance['standing']), ('HABITANTE', CURATED))
        with tempfile.TemporaryDirectory() as d:
            CurationFileTests().write(d, standing='TURISTA')
            self.assertEqual(load_curations(PACK, Path(d)), {})
            CurationFileTests().write(d, standing='VIAJANTE')
            self.assertEqual(load_curations(PACK, Path(d))['npc:cre-bernard'].standing,
                             'VIAJANTE')

    def test_knowledge_by_standing(self):
        def known(standing, homeland):
            return identity_knowledge(PACK, homeland=homeland, home='region:athkatla',
                                      campaign_year=1369, build_areas=BUILD, standing=standing)
        full, shallow = known('HABITANTE', None)
        self.assertIn('org:council-of-six', full)
        self.assertEqual(shallow, [])
        full, shallow = known('VIAJANTE', 'region:amn')
        self.assertIn('org:council-of-six', shallow)          # the place: popular core only
        self.assertIn('org:cowled-wizards', full)             # the realm it comes from
        self.assertNotIn('org:council-of-six', full)
        full, shallow = known('FORASTEIRO', 'region:tethyr')
        self.assertEqual(set(full), {'region:tethyr', 'event:tethyr-reclamation-wars-end'})
        self.assertEqual(shallow, [])

    def test_traveler_sees_only_the_popular_core(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(store.close)
        council = PACK.get('org:council-of-six')
        g = {**gen(role='PATRON'), 'standing': 'VIAJANTE', 'origin_region': 'region:amn'}
        ident = build_identity(npc_id='npc:cre-x', name='Cliente da Taverna', pack=PACK,
                               place='a Coroa de Cobre', home_region='region:athkatla',
                               resident=resident(), generated=g)
        context = build_resident_context(
            MemoryStore(store), store, Catalog.load(), npc_id='npc:cre-x',
            display_name='Cliente da Taverna', residence_areas=(), area='AR0406', dead=False,
            branch_id=ROOT_BRANCH, at_game_time=10, identity=ident, wisdom=18, intelligence=18,
            also_known=(('org:council-of-six', council.title, council.summary, council.layers),),
            popular_only_ids=frozenset({'org:council-of-six'})).context
        text = context.knowledge[0].text
        self.assertIn(council.layers['POPULAR'], text)
        self.assertNotIn('tortura', text)
        self.assertNotIn('décadas', text)
        self.assertIn('de passagem', system_prompt(context))


class OriginClaimTests(unittest.TestCase):
    """ADR-0120: what a person says about where it is from must match its standing and facts."""

    def context(self, standing, facts=('Você vive em Athkatla e está na Coroa de Cobre.',),
                staff=False, home_names=()):
        persona = Persona('npc:x', 'Nobre', (), frozenset({'Nobre'}), '...')
        return DialogueContext(
            persona, tuple(Fact(f'F{i}', f'identity:npc:x:{i}', t, 0)
                           for i, t in enumerate(facts, 1)),
            frozenset({'Nobre', 'Athkatla', 'Tethyr', 'Amn', 'Candlekeep'}), (),
            standing=standing, staff=staff, home_names=home_names)

    def check(self, speech, standing, **kw):
        raw = json.dumps({'speech': speech, 'used_facts': [], 'unknown': False},
                         ensure_ascii=False)
        return any(r.startswith('SELF_CLAIM') for r in
                   validate_reply(raw, self.context(standing, **kw)).reasons)

    def test_resident_cannot_say_it_is_from_elsewhere(self):
        self.assertTrue(self.check('Não sou de cá, mas ouvi falar.', 'HABITANTE'))
        self.assertTrue(self.check('Estou de passagem.', 'HABITANTE'))
        self.assertFalse(self.check('Moro aqui faz tempo.', 'HABITANTE'))

    def test_traveler_cannot_say_it_lives_here(self):
        self.assertTrue(self.check('Sou daqui, claro.', 'VIAJANTE'))
        self.assertTrue(self.check('Sou de aqui.', 'FORASTEIRO'))
        self.assertFalse(self.check('Não sou daqui, estou de passagem.', 'VIAJANTE'))

    def test_born_here_and_named_origin_need_the_facts(self):
        self.assertTrue(self.check('Nasci aqui.', 'HABITANTE'))
        self.assertFalse(self.check('Nasci aqui.', 'HABITANTE',
                                    facts=('Você nasceu e cresceu aqui.',)))
        self.assertTrue(self.check('Vim de Tethyr.', 'HABITANTE'))
        self.assertFalse(self.check('Vim de Tethyr há anos.', 'HABITANTE',
                                    facts=('Você veio de Tethyr e vive aqui há 9 anos.',)))

    def test_working_here_needs_a_staff_tie(self):
        self.assertTrue(self.check('Trabalho aqui como carregador.', 'HABITANTE'))
        self.assertTrue(self.check('Sou empregado da casa.', 'HABITANTE'))
        self.assertFalse(self.check('Trabalho aqui há anos.', 'HABITANTE', staff=True))
        self.assertFalse(self.check('Não trabalho aqui, só bebo.', 'HABITANTE'))
        self.assertFalse(self.check('Sou carregador no porto.', 'HABITANTE'))

    def test_staff_tie_comes_from_the_curated_affiliation(self):
        curation = SimpleNamespace(occupation='taverneiro da Coroa de Cobre', origin_region=None,
                                   years_here=None, places_visited=(), self_facts=(),
                                   affiliations=('place:copper-coronet:STAFF',),
                                   standing=None)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = CampaignStore.open(Path(tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(store.close)

        def ctx(cur):
            ident = build_identity(npc_id='npc:cre-bernard', name='Bernard', pack=PACK,
                                   place='a Coroa de Cobre', home_region='region:athkatla',
                                   resident=resident(), curation=cur)
            return build_resident_context(
                MemoryStore(store), store, Catalog.load(), npc_id='npc:cre-bernard',
                display_name='Bernard', residence_areas=(), area='AR0406', dead=False,
                branch_id=ROOT_BRANCH, at_game_time=10, identity=ident).context
        self.assertTrue(ctx(curation).staff)
        self.assertFalse(ctx(None).staff)

    def test_a_resident_may_say_it_is_from_the_regions_it_lives_in(self):
        # CR-2026-004: living in Athkatla, "sou de Amn" is true; another origin still needs facts.
        home = ('Athkatla', 'Amn')
        self.assertFalse(self.check('Sou de Amn, claro.', 'HABITANTE', home_names=home))
        self.assertFalse(self.check('Sou de Athkatla.', 'HABITANTE', home_names=home))
        self.assertTrue(self.check('Sou de Amn, claro.', 'HABITANTE'))       # no home known
        self.assertTrue(self.check('Vim de Tethyr.', 'HABITANTE', home_names=home))
        self.assertTrue(self.check('Nasci em Amn.', 'HABITANTE', home_names=home))
        self.assertFalse(self.check('Nasci em Amn.', 'HABITANTE', home_names=home,
                                    facts=('Você vive em Athkatla e está na Coroa de Cobre.',
                                           'Você nasceu e cresceu aqui.')))

    def test_home_names_come_from_the_identity_of_residents_only(self):
        def ident(standing):
            g = {**gen(role='PATRON'), 'standing': standing, 'origin_region': 'region:amn',
                 'born_here': False, 'years_here': None}
            return build_identity(npc_id='npc:cre-x', name='Cliente da Taverna', pack=PACK,
                                  place='a Coroa de Cobre', home_region='region:athkatla',
                                  resident=resident(), generated=g)
        self.assertEqual(ident('HABITANTE').home_names, ('Athkatla', 'Amn'))
        self.assertEqual(ident('VIAJANTE').home_names, ())

    def test_companions_are_not_checked(self):
        self.assertFalse(self.check('Sou de Candlekeep.', None))


class LocalAliasTests(unittest.TestCase):
    """ADR-0120 lab adjustment: "taverna", "cidade" and "reino" mean the place where one is."""

    def test_aliases_where_the_person_is(self):
        aliases = local_aliases(PACK, 'AR0406')
        self.assertEqual(aliases['taverna'], 'Coroa de Cobre')
        self.assertEqual(aliases['cidade'], 'Athkatla')
        self.assertEqual(aliases['reino'], 'Amn')
        self.assertEqual(aliases['local'], 'Coroa de Cobre')       # "o dono do local"
        self.assertEqual(local_aliases(PACK, None), {})

    def test_owner_of_this_tavern_is_heard(self):
        owner = PACK.get('rel:lehtinan-owns-copper-coronet')
        aliases = local_aliases(PACK, 'AR0406')
        known = owner.summary
        # The name came only from the question, and the speech carries the content: heard.
        self.assertIsNone(heard(owner, known, 'É Lehtinan.', 'Quem é o dono dessa taverna?',
                                aliases))
        # Without the local nouns the question names nothing.
        self.assertEqual(heard(owner, known, 'É Lehtinan.', 'Quem é o dono dessa taverna?'),
                         'NOT_SPOKEN')
        # A bare denial teaches nothing, even with the name in the question.
        self.assertEqual(heard(owner, known, 'Não sei dizer.', 'Quem é o dono dessa taverna?',
                               aliases), 'NOT_CONVEYED')

    def test_a_question_name_alone_does_not_add_undeclared_entries(self):
        held = ['rel:lehtinan-owns-copper-coronet']
        texts = {e: PACK.get(e).summary for e in held}
        aliases = local_aliases(PACK, 'AR0406')
        self.assertEqual(entries_named(PACK, held, 'É Lehtinan.', texts,
                                       question='Quem é o dono dessa taverna?', aliases=aliases),
                         [])
        self.assertEqual(entries_named(PACK, held, 'Lehtinan é o dono desta taverna.', texts,
                                       aliases=aliases), held)
