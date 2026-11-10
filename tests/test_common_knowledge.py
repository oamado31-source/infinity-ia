# SPDX-License-Identifier: Apache-2.0
"""ADR-0114 common regional knowledge: acquisition channels, pin, branches and dialogue use."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.canon.pack import KNOWLEDGE_ROOT, load_partition, load_sources  # noqa: E402
from infinity_ai.canon.pin import pin_pack  # noqa: E402
from infinity_ai.dialogue.context import Catalog, build_context  # noqa: E402
from infinity_ai.dialogue.context import build_resident_context  # noqa: E402
from infinity_ai.dialogue.engine import (  # noqa: E402
    DialogueEngine, DialogueRequest, DialogueStatus, ResidentRequest, system_prompt,
)
from infinity_ai.dialogue.llm import FakeProvider  # noqa: E402
from infinity_ai.memory.common_knowledge import (  # noqa: E402
    BackgroundRegion, Residence, acquire_common_knowledge, entries_named, identity_entries,
    placement_regions, relationship_entries, residents_as_stays, share_knowledge,
)
from infinity_ai.memory.model import KnowledgeBasis  # noqa: E402
from infinity_ai.memory.store import MemoryStore  # noqa: E402
from infinity_ai.state.recorder import ObservationRecorder  # noqa: E402
from infinity_ai.state.store import ROOT_BRANCH, CampaignStore, StoreError  # noqa: E402
from test_recorder import obs, party  # noqa: E402

PACK = load_partition(1369)
BUILD = frozenset(a for e in PACK.entries.values() for a in e.area_resrefs) | {'AR0602'}
DAY = 7200
CITY = {'region:amn', 'region:athkatla', 'org:council-of-six', 'org:cowled-wizards',
        'place:copper-coronet', 'rel:lehtinan-owns-copper-coronet'}


def reply(speech, used=(), unknown=False):
    return json.dumps({'speech': speech, 'used_facts': list(used), 'unknown': unknown},
                      ensure_ascii=False)


class Story(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = CampaignStore.open(Path(self.tmp.name) / 'c.sqlite3', 'lab')
        self.addCleanup(self.store.close)
        self.rec = ObservationRecorder(self.store)
        self.memory = MemoryStore(self.store)

    def see(self, area, t, members='["imoen","jaheira"]', epoch=0):
        return self.rec.observe(*obs(area, t, epoch=epoch), party(members, epoch=epoch))

    def pin(self, pack=PACK, game_time=None, branch=ROOT_BRANCH):
        pin_pack(self.store, branch, pack, game_time=game_time)

    def acquire(self, at, pack=PACK, branch=ROOT_BRANCH, **kw):
        return acquire_common_knowledge(self.store, branch, pack, campaign_year=1369,
                                        build_areas=BUILD, at_game_time=at, **kw)

    def known(self, npc='npc:jaheira', branch=ROOT_BRANCH, at=10**9):
        return set(self.memory.known_canon(npc, branch, at))


BERNARD = 'npc:bernard'


def lives(region='region:athkatla', since=0, evidence='GAME_DATA:AR0406', npc=BERNARD):
    return {npc: [Residence(region, since, evidence)]}


class PartyNeverLearnsByTimeTests(Story):
    def test_days_in_athkatla_teach_companions_nothing(self):
        self.see('AR0602', 100)
        self.pin(game_time=100)
        self.see('AR0406', 1000)
        report = self.acquire(1000 + 10 * DAY)
        self.assertEqual(report.status, 'OK')
        self.assertEqual(report.granted, ())
        self.assertEqual(self.known(), set())
        self.assertEqual(self.known('npc:imoen'), set())
        refused = {(r.npc_id, r.entry_id, r.reason) for r in report.refusals}
        self.assertIn(('npc:jaheira', 'org:council-of-six', 'NO_CHANNEL'), refused)

    def test_a_residence_does_not_count_while_in_the_party(self):
        self.see('AR0406', 0)
        self.pin(game_time=0)
        self.acquire(10 * DAY, residents=lives(npc='npc:jaheira'))
        self.assertEqual(self.known(), set())


class ResidenceTests(Story):
    def test_a_traveler_ignores_game_placed_residence_but_keeps_what_it_heard(self):
        # ADR-0120: the game placed it here, but it does not live here.
        self.see('AR0602', 100)
        self.pin(game_time=100)
        report = self.acquire(100 + DAY, residents=lives())
        away = frozenset({KnowledgeBasis.RESIDENCE})
        self.assertEqual(set(self.memory.known_canon(BERNARD, ROOT_BRANCH, 100 + DAY,
                                                     exclude_basis=away)), set())
        council = next(k for k in report.granted if k.entry_id == 'org:council-of-six')
        self.memory.record_canon_knowledge(
            npc_id=BERNARD, branch_id=ROOT_BRANCH, game_time=100 + DAY,
            basis=KnowledgeBasis.INQUIRY, region_id=council.region_id,
            entry_id=council.entry_id, pack_year_dr=council.pack_year_dr,
            pack_revision=council.pack_revision, pin_event_id=council.pin_event_id,
            trigger_event_id=council.trigger_event_id, title=council.title,
            summary=council.summary, layers=council.layers)
        heard = self.memory.known_canon(BERNARD, ROOT_BRANCH, 100 + DAY, exclude_basis=away)
        self.assertEqual(set(heard), {'org:council-of-six'})
        self.assertIs(heard['org:council-of-six'].basis, KnowledgeBasis.INQUIRY)

    def test_a_day_living_in_athkatla_teaches_city_and_country_common_knowledge(self):
        self.see('AR0602', 100)
        self.pin(game_time=100)
        self.assertEqual(self.acquire(100 + DAY - 1, residents=lives()).granted, ())
        report = self.acquire(100 + DAY, residents=lives())
        self.assertEqual(self.known(BERNARD), CITY)
        self.assertTrue(all(k.basis is KnowledgeBasis.RESIDENCE for k in report.granted))
        self.assertNotIn('org:shadow-thieves', self.known(BERNARD))        # CANON_REFERENCE
        self.assertNotIn('region:tethyr', self.known(BERNARD))
        self.assertEqual(self.known(), set())                              # companions: nothing

    def test_living_in_the_countryside_does_not_teach_city_specifics(self):
        self.see('AR0602', 0)
        self.pin(game_time=0)
        self.acquire(DAY, residents=lives('region:amn'))
        self.assertEqual(self.known(BERNARD), {'region:amn', 'org:cowled-wizards'})

    def test_time_in_the_party_is_not_residence(self):
        self.see('AR0602', 0)
        self.pin(game_time=0)
        self.see('AR0406', DAY // 4, '["imoen","bernard"]')
        self.see('AR0406', 3 * DAY // 4, '["imoen"]')
        self.acquire(DAY, residents=lives())
        self.assertEqual(self.known(BERNARD), set())
        self.acquire(3 * DAY // 2, residents=lives())
        self.assertEqual(self.known(BERNARD), CITY)

    def test_residence_before_the_pin_does_not_count(self):
        self.see('AR0300', 0)
        self.see('AR0300', 5 * DAY)        # no event (same area/party), just a later observation
        self.pin(game_time=5 * DAY)
        self.assertEqual(self.acquire(5 * DAY + 10, residents=lives()).granted, ())
        self.acquire(6 * DAY, residents=lives())
        self.assertEqual(self.known(BERNARD), CITY)

    def test_residence_counts_from_when_the_stay_began(self):
        self.see('AR0300', 0)
        self.pin(game_time=0)
        self.assertEqual(self.acquire(2 * DAY, residents=lives(since=DAY + 1)).granted, ())
        self.acquire(2 * DAY + 1, residents=lives(since=DAY + 1))
        self.assertEqual(self.known(BERNARD), CITY)

    def test_pin_on_an_empty_campaign_counts_from_the_first_observation(self):
        self.pin()                                      # no game time, nothing observed yet
        self.assertEqual(self.acquire(10, residents=placed('AR0406')).status, 'NO_OBSERVATION')
        self.see('AR0300', 500)
        report = self.acquire(510, residents=placed('AR0406'))
        self.assertEqual(report.status, 'OK')
        self.assertEqual(self.known(BERNARD), CITY)
        self.assertTrue(all(k.game_time == 500 for k in report.granted))   # from the first one

    def test_pin_without_game_time_anchors_on_the_last_event_before_it(self):
        self.see('AR0300', 0)
        self.pin()
        self.acquire(DAY, residents=lives())
        self.assertEqual(self.known(BERNARD), CITY)

    def test_residence_needs_evidence_and_a_known_region(self):
        self.see('AR0300', 0)
        self.pin(game_time=0)
        for stay in (lives(evidence=' '), lives('region:rashemen'), lives(since='0')):
            with self.subTest(stay=stay):
                self.acquire(10 * DAY, residents=stay)
                self.assertEqual(self.known(BERNARD), set())

    def test_idempotent(self):
        self.see('AR0300', 0)
        self.pin(game_time=0)
        first = self.acquire(DAY, residents=lives())
        self.assertEqual(len(first.granted), 6)
        self.assertEqual(self.acquire(DAY + 50, residents=lives()).granted, ())
        rows = self.store.connection.execute('SELECT count(*) FROM npc_canon_knowledge').fetchone()
        self.assertEqual(rows[0], 6)

    def test_rows_are_append_only(self):
        self.see('AR0300', 0)
        self.pin(game_time=0)
        self.acquire(DAY, residents=lives())
        with self.assertRaises(Exception):
            self.store.connection.execute("UPDATE npc_canon_knowledge SET snapshot_json = 'x'")
        with self.assertRaises(Exception):
            self.store.connection.execute('DELETE FROM npc_canon_knowledge')


FP = 'sha256:' + 'ab' * 32


def placed(*areas, npc=BERNARD):
    return residents_as_stays(PACK, {npc: SimpleNamespace(areas=areas, cre_resref='BERNAR')}, FP)


class EstablishedResidentTests(Story):
    def test_most_specific_region_for_an_area(self):
        self.assertEqual(placement_regions(PACK, 'AR0406'), ['region:athkatla'])
        self.assertEqual(placement_regions(PACK, 'ar0406'), ['region:athkatla'])
        self.assertEqual(placement_regions(PACK, 'AR0602'), [])

    def test_game_placed_resident_knows_from_the_pin(self):
        self.see('AR0602', 100)
        self.assertEqual(self.acquire(150, residents=placed('AR0406')).status, 'NOT_PINNED')
        self.pin(game_time=200)
        report = self.acquire(201, residents=placed('AR0406'))
        self.assertEqual(self.known(BERNARD), CITY)
        self.assertTrue(all(k.basis is KnowledgeBasis.RESIDENCE and k.game_time == 200
                            for k in report.granted))
        self.assertIn('GAME_DATA:AR0406#BERNAR', placed('AR0406')[BERNARD][0].evidence)

    def test_hostile_creatures_are_not_locals(self):
        monster = {'npc:ogre': SimpleNamespace(areas=('AR0406',), cre_resref='ICMIN01',
                                               allegiance=255)}
        self.assertEqual(residents_as_stays(PACK, monster, FP), {})
        bear = {'npc:cre-beargr': SimpleNamespace(areas=('AR0406',), cre_resref='BEARGR',
                                                  allegiance=128, general=2)}
        self.assertEqual(residents_as_stays(PACK, bear, FP), {})

    def test_resident_outside_the_pack_regions_knows_nothing(self):
        self.see('AR0602', 0)
        self.pin(game_time=0)
        self.assertEqual(placed('AR0602'), {})
        self.acquire(10, residents=placed('AR0602'))
        self.assertEqual(self.known(BERNARD), set())

class RelationshipAccessTests(Story):
    def test_public_relationship_is_known_in_athkatla(self):
        known = identity_entries(PACK, homeland=None, home='region:athkatla',
                                  campaign_year=1369, build_areas=BUILD)
        self.assertIn('place:copper-coronet', known)
        self.assertIn('rel:lehtinan-owns-copper-coronet', known)

    def test_operational_relationship_requires_curated_affiliation(self):
        args = dict(campaign_year=1369, build_areas=BUILD)
        staff = relationship_entries(PACK, npc_id=BERNARD,
                                     affiliations=('place:copper-coronet:STAFF',), **args)
        regular = relationship_entries(PACK, npc_id='npc:cre-regular01',
                                       affiliations=('place:copper-coronet:REGULAR',), **args)
        stranger = relationship_entries(PACK, npc_id='npc:cre-stranger',
                                         affiliations=(), **args)
        self.assertEqual(staff, ['rel:bernard-manages-copper-coronet'])
        self.assertEqual(regular, ['rel:bernard-manages-copper-coronet'])
        self.assertEqual(stranger, [])

    def test_parties_of_a_restricted_relationship_always_know_it(self):
        args = dict(campaign_year=1369, build_areas=BUILD)
        owner = relationship_entries(PACK, npc_id='npc:lehtinan', affiliations=(), **args)
        bernard_uncurated = relationship_entries(PACK, npc_id='npc:cre-bernard', affiliations=(),
                                                 **args)
        patron = relationship_entries(PACK, npc_id='npc:cre-ftown7', affiliations=(), **args)
        self.assertEqual(owner, ['rel:bernard-manages-copper-coronet'])        # the object
        self.assertEqual(bernard_uncurated, ['rel:bernard-manages-copper-coronet'])  # subject
        self.assertEqual(patron, [])

    def test_restricted_relationship_is_not_shareable_by_default(self):
        self.see('AR0406', 100, '["imoen","jaheira"]')
        self.pin(game_time=100)
        report = share_knowledge(
            self.store, ROOT_BRANCH, PACK, speaker=BERNARD, listeners=('npc:jaheira',),
            used_entry_ids=('rel:bernard-manages-copper-coronet',), req_id='rel-private-1',
            host_epoch=0, at_game_time=200,
            speech='Bernard cuida da operação da Coroa de Cobre para Lehtinan.',
            also_held=('rel:bernard-manages-copper-coronet',))
        self.assertEqual(report.status, 'NOTHING_SHARED')
        self.assertIn(('rel:bernard-manages-copper-coronet', 'SPEAKER_DOES_NOT_KNOW'),
                      {(r.entry_id, r.reason) for r in report.refusals})




class InquiryTests(Story):
    def setUp(self):
        super().setUp()
        self.see('AR0406', 100, '["imoen","jaheira","minsc"]')
        self.pin(game_time=100)
        self.acquire(110, residents=placed('AR0406'))

    def share(self, used=('org:council-of-six',), listeners=('npc:jaheira', 'npc:imoen'),
              speaker=BERNARD, req='1-2500-1', at=200, branch=ROOT_BRANCH, speech=None,
              known_texts=None):
        return share_knowledge(self.store, branch, PACK, speaker=speaker, listeners=listeners,
                               used_entry_ids=used, req_id=req, host_epoch=0, at_game_time=at,
                               speech=speech, known_texts=known_texts)

    def test_public_owner_relationship_can_be_shared_by_inquiry(self):
        entry_id = 'rel:lehtinan-owns-copper-coronet'
        speech = 'Lehtinan é o dono da Coroa de Cobre.'
        known_texts = {entry_id: PACK.get(entry_id).layers['POPULAR']}
        self.assertEqual(entries_named(PACK, (entry_id,), speech, known_texts), [entry_id])
        report = self.share(used=(entry_id,), req='owner-1', speech=speech,
                            known_texts=known_texts)
        self.assertEqual(report.status, 'OK')
        self.assertIn(entry_id, self.known('npc:jaheira'))
        self.assertTrue(all(k.basis is KnowledgeBasis.INQUIRY for k in report.granted))

    def test_listeners_learn_only_what_was_used(self):
        report = self.share()
        self.assertEqual(report.status, 'OK')
        self.assertEqual(self.known(), {'org:council-of-six'})
        self.assertEqual(self.known('npc:imoen'), {'org:council-of-six'})
        self.assertEqual(self.known('npc:minsc'), set())               # out of earshot
        self.assertTrue(all(k.basis is KnowledgeBasis.INQUIRY for k in report.granted))
        self.assertEqual(report.event.event_type, 'KnowledgeShared')
        self.assertNotIn('text', report.event.payload)

    def test_only_entries_named_in_the_speech_are_learned(self):
        report = share_knowledge(
            self.store, ROOT_BRANCH, PACK, speaker=BERNARD, listeners=('npc:jaheira',),
            used_entry_ids=('org:council-of-six', 'org:cowled-wizards'), req_id='1-3000-9',
            host_epoch=0, at_game_time=200,
            speech='Quem manda é o Conselho dos Seis, e ninguém sabe quem são.')
        self.assertEqual(self.known(), {'org:council-of-six'})
        self.assertIn(('org:cowled-wizards', 'NOT_SPOKEN'),
                      {(r.entry_id, r.reason) for r in report.refusals})
        silent = share_knowledge(
            self.store, ROOT_BRANCH, PACK, speaker=BERNARD, listeners=('npc:imoen',),
            used_entry_ids=('org:cowled-wizards',), req_id='1-3100-10', host_epoch=0,
            at_game_time=200, speech='Acha? Eu não acho nada.')
        self.assertEqual(silent.status, 'NOTHING_SHARED')
        self.assertEqual(self.known('npc:imoen'), set())

    def test_named_but_undeclared_entries_count_as_heard(self):
        held = self.memory.known_canon(BERNARD, ROOT_BRANCH, 200)
        said = 'Sim, ouvi falar. É o governo de Amn, mas não sou amigo dos políticos.'
        self.assertEqual(entries_named(PACK, held, said), ['region:amn'])
        self.assertEqual(entries_named(PACK, held, 'O Conselho dos Seis manda.'),
                         ['org:council-of-six'])
        self.assertEqual(entries_named(PACK, ['org:shadow-thieves'], 'Ladrões das Sombras'), [])

    def test_speaker_must_know_the_entry(self):
        report = self.share(used=('org:shadow-thieves', 'region:tethyr'))
        self.assertEqual(report.status, 'NOTHING_SHARED')
        self.assertEqual({r.reason for r in report.refusals}, {'SPEAKER_DOES_NOT_KNOW'})
        self.assertEqual(self.known(), set())

    def test_listener_must_be_in_the_party_and_not_the_speaker(self):
        report = self.share(listeners=('npc:viconia', BERNARD))
        self.assertEqual(report.status, 'NOTHING_SHARED')
        self.assertEqual(self.known('npc:viconia'), set())

    def test_a_companion_never_teaches_another(self):
        self.share()
        report = self.share(speaker='npc:jaheira', listeners=('npc:minsc',), req='1-2600-2')
        self.assertEqual(report.status, 'SPEAKER_IN_PARTY')     # Jaheira knows it, still refused
        self.assertEqual(self.known('npc:minsc'), set())

    def test_idempotent_per_request(self):
        first = self.share()
        again = self.share()
        self.assertEqual(len(first.granted), 2)
        self.assertEqual(again.granted, ())
        self.assertEqual(again.event.event_id, first.event.event_id)

    def test_fork_before_the_conversation_does_not_know(self):
        self.see('AR0406', 300, '["imoen","jaheira","minsc"]')
        self.share(at=300)
        child = self.see('AR0406', 250, '["imoen","jaheira","minsc"]', epoch=1).branch_id
        self.assertNotEqual(child, ROOT_BRANCH)
        self.assertEqual(self.known(branch=child), set())
        self.assertEqual(self.known(), {'org:council-of-six'})

    def test_nothing_without_pin(self):
        other = CampaignStore.open(Path(self.tmp.name) / 'd.sqlite3', 'lab2')
        self.addCleanup(other.close)
        report = share_knowledge(other, ROOT_BRANCH, PACK, speaker=BERNARD,
                                 listeners=('npc:jaheira',), used_entry_ids=('org:council-of-six',),
                                 req_id='1-1-1', host_epoch=0, at_game_time=1)
        self.assertEqual(report.status, 'NOT_PINNED')


class PinAndRevisionTests(Story):
    def setUp(self):
        super().setUp()
        kdir = tempfile.TemporaryDirectory()
        self.addCleanup(kdir.cleanup)
        self.kroot = Path(kdir.name) / 'knowledge'
        shutil.copytree(KNOWLEDGE_ROOT, self.kroot)

    def corrected_pack(self):
        path = self.kroot / 'periods' / '1369-DR' / 'organizations' / 'council-of-six.json'
        doc = json.loads(path.read_text(encoding='utf-8'))
        doc['summary'] = 'Versão corrigida do resumo.'
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        return load_partition(1369, self.kroot)

    def test_nothing_without_a_matching_pin(self):
        self.see('AR0300', 0)
        self.assertEqual(self.acquire(DAY, residents=lives()).status, 'NOT_PINNED')
        self.pin(game_time=0)
        changed = self.corrected_pack()
        self.assertEqual(self.acquire(DAY, pack=changed, residents=lives()).status,
                         'REVISION_CHANGED')
        self.assertEqual(self.known(BERNARD), set())

    def test_correction_after_repin_keeps_what_was_learned(self):
        self.see('AR0300', 0)
        self.pin(game_time=0)
        self.acquire(DAY, residents=lives())
        changed = self.corrected_pack()
        self.pin(changed, game_time=DAY)
        self.acquire(3 * DAY, pack=changed, residents=lives())
        council = self.memory.known_canon(BERNARD, ROOT_BRANCH)['org:council-of-six']
        self.assertNotIn('corrigida', council.summary)
        self.assertEqual(council.pack_revision, PACK.revision)


class BranchTests(Story):
    def test_fork_before_the_threshold_does_not_know(self):
        self.see('AR0300', 0)
        self.pin(game_time=0)
        self.see('AR0400', DAY)
        self.acquire(DAY, residents=lives())
        child = self.see('AR0300', DAY // 2, epoch=1).branch_id
        self.assertNotEqual(child, ROOT_BRANCH)
        self.assertEqual(self.known(BERNARD, branch=child), set())
        self.assertEqual(self.known(BERNARD, branch=ROOT_BRANCH), CITY)
        _, _, held = self.memory.recall_common(npc_id=BERNARD, branch_id=child,
                                               at_game_time=DAY // 2, purpose='npc_dialogue',
                                               audience='NARRATIVE_CONTEXT')
        self.assertEqual(held, ())

    def test_recall_gates(self):
        status, reason, _ = self.memory.recall_common(
            npc_id='npc:jaheira', branch_id=ROOT_BRANCH, at_game_time=1, purpose='debug',
            audience='NARRATIVE_CONTEXT')
        self.assertEqual(reason, 'ACL_PURPOSE')
        status, reason, _ = self.memory.recall_common(
            npc_id='npc:jaheira', branch_id='nope', at_game_time=1, purpose='npc_dialogue',
            audience='NARRATIVE_CONTEXT')
        self.assertEqual(reason, 'UNKNOWN_BRANCH')

    def test_write_requires_visible_events(self):
        self.see('AR0300', 0)
        with self.assertRaises(StoreError):
            self.memory.record_canon_knowledge(
                npc_id='npc:jaheira', branch_id=ROOT_BRANCH, game_time=1,
                basis=KnowledgeBasis.ORIGIN, region_id='region:amn', entry_id='region:amn',
                pack_year_dr=1369, pack_revision=PACK.revision, pin_event_id='ev-missing',
                trigger_event_id='ev-missing', title='t', summary='s')


class OriginTests(Story):
    def background(self, **over):
        b = dict(region_id='region:tethyr', source_id='bg2-manual', locator='p. 31',
                 checked_by='mantenedor', checked_at='2026-11-09')
        b.update(over)
        return {'npc:jaheira': [BackgroundRegion(**b)]}

    def test_curated_origin_is_known_from_the_first_appearance(self):
        self.see('AR0602', 100)
        self.pin(game_time=100)
        report = self.acquire(150, backgrounds=self.background(), sources=load_sources())
        self.assertEqual(self.known(), {'region:tethyr', 'event:tethyr-reclamation-wars-end'})
        self.assertTrue(all(k.basis is KnowledgeBasis.ORIGIN and k.game_time == 100
                            for k in report.granted))
        self.assertEqual(self.known('npc:imoen'), set())

    def test_origin_also_holds_for_npcs_outside_the_party(self):
        self.see('AR0602', 100)
        self.pin(game_time=100)
        b = self.background()['npc:jaheira']
        report = self.acquire(150, backgrounds={BERNARD: b}, sources=load_sources())
        self.assertEqual(self.known(BERNARD), {'region:tethyr', 'event:tethyr-reclamation-wars-end'})
        self.assertTrue(all(k.game_time == 100 for k in report.granted))   # from the pin

    def test_origin_needs_a_checked_strong_source(self):
        self.see('AR0602', 100)
        self.pin(game_time=100)
        for over in ({'checked_by': ''}, {'locator': ' '}, {'source_id': 'unknown'},
                     {'region_id': 'region:rashemen'}):
            with self.subTest(over=over):
                self.acquire(150, backgrounds=self.background(**over), sources=load_sources())
                self.assertEqual(self.known(), set())


class DialogueTests(Story):
    def setUp(self):
        super().setUp()
        self.see('AR0602', 0)
        self.pin(game_time=0)
        self.see('AR0300', 10)

    def learn(self):
        amn = BackgroundRegion('region:amn', 'bg2-manual', 'p. 0 (sintético)', 'teste', '2026-11-09')
        return self.acquire(10 + DAY, backgrounds={'npc:jaheira': [amn]}, sources=load_sources())

    def ctx(self, at):
        return build_context(self.memory, self.store, Catalog.load(), npc_id='npc:jaheira',
                             branch_id=ROOT_BRANCH, at_game_time=at).context

    def test_knowledge_reaches_the_prompt_only_after_acquisition(self):
        before = self.ctx(100)
        self.assertEqual(before.knowledge, ())
        self.assertIn('você não conhece a região', system_prompt(before))
        self.learn()
        after = self.ctx(10 + DAY)
        texts = {k.fact_id: k.text for k in after.knowledge}
        self.assertEqual(len(texts), 6)
        self.assertIn('canon:place:copper-coronet',
                      {k.event_id for k in after.knowledge})
        self.assertIn('canon:rel:lehtinan-owns-copper-coronet',
                      {k.event_id for k in after.knowledge})
        self.assertTrue(any(t.startswith('Conselho dos Seis:') for t in texts.values()))
        self.assertIn('CONHECIMENTO GERAL:\nK1:', system_prompt(after))
        self.assertTrue({'Amn', 'Athkatla', 'Conselho', 'Seis'} <= after.vocabulary)

    def test_companion_ability_scores_set_the_depth_in_the_box(self):
        self.learn()
        def council(**scores):
            ctx = build_context(self.memory, self.store, Catalog.load(), npc_id='npc:jaheira',
                                branch_id=ROOT_BRANCH, at_game_time=10 + DAY, **scores).context
            text = next(k.text for k in ctx.knowledge if k.event_id == 'canon:org:council-of-six')
            return ctx, text
        # Overlay (no scores): the whole checked summary, as before.
        ctx, full = council()
        self.assertIn('três décadas', full)
        self.assertIsNone(ctx.manner)
        # Box, low Wisdom and Intelligence: only the popular core, rudimentary manner.
        ctx, low = council(wisdom=6, intelligence=8)
        self.assertNotIn('décadas', low)
        self.assertNotIn('Meisarch', low)
        self.assertNotIn('Meisarch', ctx.vocabulary)
        self.assertIn('Como você fala e pensa:', system_prompt(ctx))
        # A studious companion reaches the studied layer.
        _, studied = council(wisdom=14, intelligence=17)
        self.assertIn('três décadas', studied)

    def test_engine_maps_k_ids_and_rejects_raw_ids(self):
        self.learn()
        council = next(k.fact_id for k in self.ctx(10 + DAY).knowledge
                       if k.event_id == 'canon:org:council-of-six')
        engine = DialogueEngine(self.store, FakeProvider([
            reply(f'Segundo {council}, quem manda é o Conselho.', [council]),
            reply('Quem manda em Amn é o Conselho dos Seis, gente sem rosto.', [council])]),
            Catalog.load())
        result = engine.respond(DialogueRequest('npc:jaheira', 'Quem governa aqui?'),
                                branch_id=ROOT_BRANCH, at_game_time=10 + DAY)
        self.assertEqual(result.status, DialogueStatus.OK)
        self.assertEqual(result.used_event_ids, ('canon:org:council-of-six',))
        self.assertTrue(any('META_TALK' in f for f in result.flags))

    def test_without_acquisition_the_council_is_an_unknown_name(self):
        self.acquire(10 + 10 * DAY)                    # days in Athkatla, no origin: nothing
        engine = DialogueEngine(self.store, FakeProvider([
            reply('O Conselho dos Seis manda aqui.', []),
            reply('O Conselho dos Seis manda aqui.', [])]), Catalog.load())
        result = engine.respond(DialogueRequest('npc:jaheira', 'Quem governa?'),
                                branch_id=ROOT_BRANCH, at_game_time=10 + 10 * DAY)
        self.assertEqual(result.status, DialogueStatus.FALLBACK)
        self.assertTrue(any('UNKNOWN_NAMES' in f for f in result.flags))


class ResidentDialogueTests(Story):
    def setUp(self):
        super().setUp()
        self.see('AR0406', 100, '["imoen","jaheira"]')
        self.pin(game_time=100)

    def ctx(self, **over):
        kw = dict(npc_id=BERNARD, display_name='Bernard', residence_areas=('AR0406',),
                  area='AR0406', dead=False, branch_id=ROOT_BRANCH, at_game_time=200, wisdom=18)
        kw.update(over)
        return build_resident_context(self.memory, self.store, Catalog.load(), **kw)

    def test_gates(self):
        stranger = self.ctx(npc_id='npc:cre-ftown7', display_name='Cliente', residence_areas=())
        self.assertEqual(stranger.reason, 'OK')                 # anyone alive may talk ...
        self.assertEqual(stranger.context.knowledge, ())        # ... but knows nothing
        self.assertEqual(self.ctx(dead=True).reason, 'SPEAKER_DEAD')
        self.assertEqual(self.ctx(area='AR0300').reason, 'NPC_NOT_PRESENT')
        self.assertEqual(self.ctx(area=None).reason, 'NPC_NOT_PRESENT')

    def test_resident_prompt_has_only_common_knowledge(self):
        self.acquire(110, residents=placed('AR0406'))
        context = self.ctx().context
        self.assertEqual(context.facts, ())
        self.assertEqual(len(context.knowledge), 6)
        prompt = system_prompt(context)
        self.assertIn('Você é Bernard e está na Coroa de Cobre', prompt)
        self.assertNotIn('companheiro(a) de viagem', prompt)
        self.assertNotIn('Orientação:', prompt)

    def test_wisdom_sets_depth_not_number_of_subjects(self):
        self.acquire(110, residents=placed('AR0406'))
        dull = self.ctx(wisdom=5).context
        wise = self.ctx(wisdom=18, intelligence=14).context
        self.assertEqual(len(dull.knowledge), len(wise.knowledge))           # all subjects known
        council = {k.event_id: k.text for k in dull.knowledge}['canon:org:council-of-six']
        self.assertEqual(council, 'Conselho dos Seis: É quem governa Amn; ninguém sabe quem são '
                                  'os seis conselheiros.')
        deep = {k.event_id: k.text for k in wise.knowledge}['canon:org:council-of-six']
        self.assertIn('Meisarch', deep)
        self.assertIn('muito simples', system_prompt(dull))
        self.assertIn('profundidade', system_prompt(wise))

    def test_knowledge_learned_before_layers_uses_the_same_summary_layers(self):
        pin = self.store.visible_events(ROOT_BRANCH, 'KnowledgePackPinned')[-1]
        council = PACK.get('org:council-of-six')
        self.memory.record_canon_knowledge(
            npc_id=BERNARD, branch_id=ROOT_BRANCH, game_time=150, basis=KnowledgeBasis.RESIDENCE,
            region_id='region:athkatla', entry_id=council.id, pack_year_dr=1369,
            pack_revision=PACK.revision, pin_event_id=pin.event_id, trigger_event_id=pin.event_id,
            title=council.title, summary=council.summary)                   # no layers stored
        same = ((council.id, council.title, council.summary, council.layers),)
        text = self.ctx(wisdom=5, also_known=same).context.knowledge[0].text
        self.assertEqual(text, f"Conselho dos Seis: {council.layers['POPULAR']}")
        changed = ((council.id, council.title, 'Outro resumo.', council.layers),)
        kept = self.ctx(wisdom=5, also_known=changed).context.knowledge[0].text
        self.assertEqual(kept, 'Conselho dos Seis: Governa Amn há cerca de três décadas.')

    def test_profile_sets_style_and_orientation_not_facts(self):
        from infinity_ai.personality import generate_new_npc_profile
        profile = generate_new_npc_profile(npc_id='npc:generated:enc-x', campaign_id='lab',
                                           creation_branch_id=ROOT_BRANCH, world_seed='w',
                                           npc_origin='CREATED')
        plain = self.ctx(npc_id='npc:cre-ftown7', display_name='Cliente', residence_areas=())
        shaped = self.ctx(npc_id='npc:cre-ftown7', display_name='Cliente', residence_areas=(),
                          profile=profile)
        self.assertEqual(len(shaped.context.persona.style), 6)
        self.assertNotEqual(shaped.context.persona.style, plain.context.persona.style)
        self.assertIn('Orientação:', system_prompt(shaped.context))
        self.assertEqual(shaped.context.knowledge, ())

    def engine(self, *replies):
        return DialogueEngine(self.store, FakeProvider([reply(*r) for r in replies]),
                              Catalog.load())

    def test_answer_reports_the_entries_used_and_teaches_listeners(self):
        self.acquire(110, residents=placed('AR0406'))
        council = next(k.fact_id for k in self.ctx().context.knowledge
                       if k.event_id == 'canon:org:council-of-six')
        result = self.engine(('Quem manda é o Conselho dos Seis, e ninguém sabe quem são.',
                              [council])).respond_resident(
            ResidentRequest(BERNARD, 'Bernard', 'Quem governa Amn?', 'AR0406', False),
            residence_areas=('AR0406',), branch_id=ROOT_BRANCH, at_game_time=200)
        self.assertEqual(result.status, DialogueStatus.OK)
        self.assertEqual(result.used_event_ids, ('canon:org:council-of-six',))
        used = [e.split(':', 1)[1] for e in result.used_event_ids]
        share_knowledge(self.store, ROOT_BRANCH, PACK, speaker=BERNARD,
                        listeners=('npc:jaheira',), used_entry_ids=used, req_id='1-1-1',
                        host_epoch=0, at_game_time=200)
        self.assertEqual(self.known(), {'org:council-of-six'})
        self.assertEqual(self.known('npc:imoen'), set())

    def test_resident_without_knowledge_cannot_name_the_council(self):
        result = self.engine(('O Conselho dos Seis.', []), ('O Conselho dos Seis.', [])
                             ).respond_resident(
            ResidentRequest(BERNARD, 'Bernard', 'Quem governa Amn?', 'AR0406', False),
            residence_areas=('AR0406',), branch_id=ROOT_BRANCH, at_game_time=200)
        self.assertEqual(result.status, DialogueStatus.FALLBACK)
        self.assertEqual(result.speech, 'Hum? Disso eu não sei.')


if __name__ == '__main__':
    unittest.main()
