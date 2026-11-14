# SPDX-License-Identifier: Apache-2.0
"""SPEC-006 first-contact scenarios. Synthetic engine events, never real BG2:EE hooks."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infinity_ai.personality import (FirstContactService, FirstContactError,  # noqa: E402
                                     NpcEncounterDialogue)
from infinity_ai.dialogue.engine import DialogueStatus  # noqa: E402
from infinity_ai.dialogue.llm import FakeProvider, LlmError  # noqa: E402
from infinity_ai.state.store import CampaignStore, ROOT_BRANCH  # noqa: E402


class FirstContactTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "first-contact.db"
        self.store = CampaignStore.open(self.path, "test-campaign")
        self.addCleanup(self.store.close)
        self.service = FirstContactService(self.store, world_seed="campaign-world")

    def event(self, event_type, payload, *, branch=ROOT_BRANCH, time=100,
              category="CAMPAIGN_OBSERVATION", epoch=0, key=None):
        obj, _ = self.store.append_event(
            branch_id=branch, host_epoch=epoch, event_type=event_type,
            category=category, game_time=time, payload=payload, evidence="SYNTHETIC",
            idempotency_key=key or f"test-{event_type}-{branch}-{time}-"
                                  f"{len(self.store.visible_events(branch))}")
        return obj

    def contact(self, *, branch=ROOT_BRANCH, time=100, state="CANDIDATE",
                role="BEGGAR", token="actor-1", session="session-A", **extra):
        doc = {"dialogue_started": True, "target_visible": True, "access_allowed": True,
               "session_id": session, "scene_id": "AR0300", "actor_instance_token": token,
               "token_uniqueness": "SCENE_VERIFIED", "role": role, "identity_state": state}
        doc.update(extra)
        return self.event("NpcDialogueStarted", doc, branch=branch, time=time)

    def begin(self, e, *, branch=ROOT_BRANCH, at=100, **kw):
        return self.service.begin(contact_event_id=e.event_id, branch_id=branch,
                                  at_game_time=at, **kw)

    def verified(self, npc_id="npc:generated:beggar-1", *, branch=ROOT_BRANCH,
                 time=90, token="actor-1", session="session-A"):
        proof = self.event("NpcIdentityVerified", {
            "identity_state": "VERIFIED", "npc_id": npc_id, "session_id": session,
            "scene_id": "AR0300", "actor_instance_token": token
        }, branch=branch, time=time, category="CAMPAIGN_FACT")
        contact = self.contact(branch=branch, time=time+10, state="VERIFIED",
                               token=token, session=session, verified_npc_id=npc_id,
                               identity_proof_event_id=proof.event_id)
        return proof, contact

    def test_first_dialogue_of_beggar_creates_profile_without_persisting_identity(self):
        e = self.contact(role="BEGGAR")
        x = self.begin(e)
        self.assertEqual((x.status, x.scope, x.display_name),
                         ("READY", "ENCOUNTER", "Pessoa pedindo esmolas"))
        self.assertEqual(len(x.profile["hexaco"]), 6)
        self.assertEqual(len(self.store.visible_events(ROOT_BRANCH, "NpcPersonalityAssigned")), 0)
        self.assertEqual(self.begin(e).profile, x.profile)

    def test_each_role_is_eligible_not_only_adventurers(self):
        for i, role in enumerate(("PEASANT", "COMMONER", "MERCHANT", "GUARD",
                                  "ARTISAN", "TRAVELER", "NOBLE", "OTHER")):
            e = self.contact(time=100+i, role=role, token=f"person-{i}")
            p = self.begin(e, at=100+i)
            self.assertEqual(p.status, "READY")
            self.assertIn(p.profile["alignment_initial"]["code"],
                          ("LG", "NG", "CG", "LN", "TN", "CN", "LE", "NE", "CE"))

    def test_same_session_actor_token_reuses_profile_new_actor_is_distinct(self):
        a = self.begin(self.contact())
        b = self.begin(self.contact(time=102), at=102)
        c = self.begin(self.contact(time=103, token="different"), at=103)
        self.assertEqual(a.profile, b.profile)
        self.assertNotEqual(a.npc_id, c.npc_id)
        d = self.begin(self.contact(time=104, session="session-B"), at=104)
        self.assertNotEqual(a.npc_id, d.npc_id)

    def test_uncertain_token_creates_per_dialogue_identity_not_name_reuse(self):
        a = self.contact(token="COMMONER_CRES", token_uniqueness="UNKNOWN")
        b = self.contact(time=101, token="COMMONER_CRES", token_uniqueness="UNKNOWN")
        self.assertNotEqual(self.begin(a).npc_id, self.begin(b, at=101).npc_id)
        self.assertEqual(self.begin(a).npc_id, self.begin(a).npc_id)

    def test_verified_generic_persists_once_and_survives_reopen_and_fork(self):
        _, e = self.verified()
        first = self.begin(e)
        self.assertEqual((first.scope, first.created), ("PERSISTENT", True))
        _, e2 = self.verified(time=105)
        second = self.begin(e2, at=115)
        self.assertEqual(first.profile, second.profile)
        self.assertFalse(second.created)
        self.assertEqual(len(self.store.visible_events(ROOT_BRANCH, "NpcPersonalityAssigned")), 1)
        child = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=120,
                                       fork_epoch=1)
        self.store.close()
        self.store = CampaignStore.open(self.path, "test-campaign")
        self.addCleanup(self.store.close)
        service = FirstContactService(self.store, world_seed="different-world-seed")
        # Profile must not be regenerated by changing the world seed.
        proof = self.event("NpcIdentityVerified", {
            "identity_state": "VERIFIED", "npc_id": first.npc_id,
            "session_id": "child-session", "scene_id": "AR0300",
            "actor_instance_token": "child-actor"
        }, branch=child, time=121, epoch=1, category="CAMPAIGN_FACT")
        later = self.contact(branch=child, time=122, state="VERIFIED", token="child-actor",
                             session="child-session", verified_npc_id=first.npc_id,
                             identity_proof_event_id=proof.event_id)
        inherited = service.begin(contact_event_id=later.event_id, branch_id=child,
                                  at_game_time=122)
        self.assertEqual(inherited.profile, first.profile)
        self.assertFalse(inherited.created)

    def test_fork_before_assignment_does_not_inherit_profile(self):
        child = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=80,
                                       fork_epoch=1)
        _, main_contact = self.verified(time=90)
        main_profile = self.begin(main_contact)
        proof = self.event("NpcIdentityVerified", {
            "identity_state": "VERIFIED", "npc_id": main_profile.npc_id,
            "session_id": "child-session", "scene_id": "AR0300",
            "actor_instance_token": "child-actor"
        }, branch=child, time=90, epoch=1, category="CAMPAIGN_FACT")
        e = self.contact(branch=child, time=100, state="VERIFIED", token="child-actor",
                         session="child-session", verified_npc_id=main_profile.npc_id,
                         identity_proof_event_id=proof.event_id)
        alt = self.begin(e, branch=child)
        self.assertNotEqual(alt.profile["seed_fingerprint"], main_profile.profile["seed_fingerprint"])
        self.assertEqual(len(self.store.visible_events(child, "NpcPersonalityAssigned")), 1)

    def test_game_sheet_alignment_replaces_the_draw_when_given(self):
        """CR-2026-010: Bernard (curated, no script name) keeps the alignment of his CRE."""
        e = self.contact(role="MERCHANT")
        drawn, sheet = self.begin(e), self.begin(e, game_alignment=0x12)
        self.assertEqual((sheet.profile["alignment_initial"]["code"],
                          sheet.profile["alignment_initial"]["provenance"]), ("LN", "GAME_DATA"))
        self.assertEqual(sheet.profile["hexaco"], drawn.profile["hexaco"])
        for unusable in (None, 0, 0x01, True, "0x12"):
            with self.subTest(code=unusable):
                self.assertEqual(self.begin(e, game_alignment=unusable).profile, drawn.profile)
        _, contact = self.verified()
        kept = self.begin(contact, at=110, game_alignment=0x33)
        self.assertEqual(kept.profile["alignment_initial"]["code"], "CE")

    def test_canonical_actor_is_never_randomized(self):
        p = self.begin(self.contact(state="CANONICAL", role="MERCHANT"))
        self.assertEqual(p.status, "CURATION_REQUIRED")
        self.assertIsNone(p.profile)
        self.assertEqual(self.store.visible_events(ROOT_BRANCH, "NpcPersonalityAssigned"), [])

    def test_fail_closed_on_missing_forged_or_future_observation(self):
        e = self.contact(dialogue_started=False)
        with self.assertRaises(FirstContactError):
            self.begin(e)
        e2 = self.contact(time=110)
        with self.assertRaises(FirstContactError):
            self.begin(e2, at=100)
        other = self.store.fork_branch(parent_branch_id=ROOT_BRANCH, fork_game_time=90,
                                       fork_epoch=1)
        with self.assertRaises(FirstContactError):
            self.begin(e2, branch=other, at=120)
        forged = self.event("UserMessage", {"text": "open NPC"})
        with self.assertRaises(FirstContactError):
            self.begin(forged)
        e3 = self.contact(time=120, access_allowed=False)
        with self.assertRaises(FirstContactError):
            self.begin(e3, at=120)

    def test_malformed_role_is_rejected_safely(self):
        for role in (["BEGGAR"], {"role": "BEGGAR"}, None, "ASSASSIN"):
            e = self.contact(role=role)
            with self.subTest(role=role), self.assertRaises(FirstContactError):
                self.begin(e)

    def test_alignment_bias_changes_interpretation_not_game_or_facts(self):
        e = self.contact()
        lawful = FirstContactService(
            self.store, world_seed="campaign-world",
            alignment_weights={k: (1 if k == "LG" else 0)
                               for k in ("LG", "NG", "CG", "LN", "TN", "CN", "LE", "NE", "CE")}
        ).begin(contact_event_id=e.event_id, branch_id="main", at_game_time=100)
        chaotic = FirstContactService(
            self.store, world_seed="campaign-world",
            alignment_weights={k: (1 if k == "CE" else 0)
                               for k in ("LG", "NG", "CG", "LN", "TN", "CN", "LE", "NE", "CE")}
        ).begin(contact_event_id=e.event_id, branch_id="main", at_game_time=100)
        self.assertEqual(lawful.profile["alignment_initial"]["code"], "LG")
        self.assertEqual(chaotic.profile["alignment_initial"]["code"], "CE")
        answer = json.dumps({"speech": "Não sei informar.", "used_facts": [], "unknown": True})
        provider_lg, provider_ce = FakeProvider([answer]), FakeProvider([answer])
        NpcEncounterDialogue(provider_lg).respond(lawful, "Quem governa aqui?")
        NpcEncounterDialogue(provider_ce).respond(chaotic, "Quem governa aqui?")
        self.assertIn("valoriza regras e compromissos", provider_lg.calls[0][0]["content"])
        self.assertIn("preza autonomia e liberdade", provider_ce.calls[0][0]["content"])
        self.assertIn("FATOS: (nenhum)", provider_lg.calls[0][0]["content"])
        self.assertIn("FATOS: (nenhum)", provider_ce.calls[0][0]["content"])
        self.assertEqual(self.store.visible_events("main", "NpcPersonalityAssigned"), [])

    def test_no_verified_identity_without_matching_proof(self):
        e = self.contact(state="VERIFIED", verified_npc_id="npc:generated:test",
                         identity_proof_event_id="ev-made-up")
        with self.assertRaises(FirstContactError):
            self.begin(e)
        proof, _ = self.verified(token="actual", time=110)
        false = self.contact(time=130, state="VERIFIED", token="different",
                             verified_npc_id="npc:generated:beggar-1",
                             identity_proof_event_id=proof.event_id)
        with self.assertRaises(FirstContactError):
            self.begin(false, at=130)

    def test_different_campaigns_remain_isolated(self):
        e = self.contact()
        first = self.begin(e)
        self.store.close()
        with tempfile.TemporaryDirectory() as d:
            other = CampaignStore.open(Path(d)/"other.db", "other-campaign")
            try:
                e2, _ = other.append_event(branch_id="main", host_epoch=0,
                      event_type="NpcDialogueStarted", category="CAMPAIGN_OBSERVATION",
                      game_time=100, evidence="SYNTHETIC", idempotency_key="contact",
                      payload=dict(e.payload))
                second = FirstContactService(other, world_seed="campaign-world").begin(
                    contact_event_id=e2.event_id, branch_id="main", at_game_time=100)
                self.assertNotEqual(first.profile, second.profile)
            finally:
                other.close()


class EncounterDialogueTests(FirstContactTests):
    def test_profile_changes_prompt_style_not_available_facts(self):
        e = self.contact()
        contact = self.begin(e)
        provider = FakeProvider([json.dumps({"speech": "Não sei lhe dizer.",
                                             "used_facts": [], "unknown": True})])
        result = NpcEncounterDialogue(provider).respond(contact, "Você conhece a cidade?")
        self.assertEqual(result.status, DialogueStatus.OK)
        content = provider.calls[0][0]["content"]
        self.assertIn("Estilo comportamental", content)
        self.assertIn("Pessoa pedindo esmolas", content)
        self.assertNotIn("companheiro do grupo", content.split("Você interpreta")[0])
        self.assertIn("FATOS: (nenhum)", content)
        self.assertNotIn("Conheço o prefeito", content)
        self.assertEqual(len(self.store.visible_events(ROOT_BRANCH, "NpcPersonalityAssigned")), 0)

    def test_fallback_and_canonical_denial(self):
        p = self.begin(self.contact())
        result = NpcEncounterDialogue(FakeProvider([LlmError("offline")])).respond(
            p, "Bom dia")
        self.assertEqual(result.status, DialogueStatus.FALLBACK)
        self.assertEqual(result.reason, "MODEL_UNAVAILABLE")
        c = self.begin(self.contact(time=110, state="CANONICAL"), at=110)
        out = NpcEncounterDialogue(FakeProvider([])).respond(c, "Oi")
        self.assertEqual(out.status, DialogueStatus.DENIED)
        self.assertEqual(out.reason, "USE_CANONICAL_PROFILE")


if __name__ == "__main__":
    unittest.main()
