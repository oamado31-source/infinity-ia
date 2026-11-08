"""DEC-106/C — Synthetic-only reputation rehabilitation eligibility planner.

No BG2:EE, EEex, host, NPC belief write, public notice, economy, item,
reputation-score or LLM integration. Trusted_* stores are test-fixture inputs;
a production implementation MUST authenticate them independently of a request.
"""
from __future__ import annotations
import hashlib
import json

_SCOPE = ("campaign_id", "branch_id", "lineage_id", "build_fingerprint", "modpack_hash", "host_epoch", "checkpoint_epoch")
_CLASSIFICATION = {"PUBLIC": 0, "RESTRICTED": 1, "PROTECTED": 2}
_ALLOWED_REQUEST = frozenset(("case_ref", "subject_ref", "audience", "purpose", "expected_revision", "trace_ref"))
_BELIEFS = frozenset(("NEVER_HEARD", "HEARD_UNASSESSED", "BELIEVES_PRIOR", "DOUBTS_PRIOR", "CONTESTED", "REVISED"))
_TRUST = frozenset(("UNREVIEWED", "BROKEN", "CONTESTED", "WILLING_TO_REENGAGE", "UNCHANGED"))
_DAMAGE = frozenset(("NONE", "ALLEGED", "DISPUTED", "CORROBORATED", "HOST_CONFIRMED"))
_DELIVERY = frozenset(("NOT_SENT", "QUEUED", "IN_TRANSIT", "LOST", "DELIVERED", "UNCERTAIN"))


def _out(status: str, reason: str, **detail: object) -> dict:
    return dict(status=status, reason=reason, proposal_only=True, host_calls=0,
                currency_transferred=0, reputation_points_written=0,
                npcs_compelled=0, notices_sent=0, facts_erased=0,
                stored_events_mutated=False, **detail)


def _hash(*components: object) -> str:
    blob = json.dumps(components, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _scope_matches(obj: object, scope: dict) -> bool:
    return isinstance(obj, dict) and all(obj.get(k) == scope.get(k) for k in _SCOPE)


def _valid_scope(ctx: object) -> bool:
    if not isinstance(ctx, dict) or ctx.get("fixture_only") is not True or ctx.get("host_mode") != "SYNTHETIC_HOST_FIXTURE":
        return False
    if any(not isinstance(ctx.get(k), str) or not ctx[k].startswith("SYN-") for k in _SCOPE[:5]):
        return False
    if any(type(ctx.get(k)) is not int or ctx[k] < 0 for k in _SCOPE[5:]):
        return False
    return type(ctx.get("world_tick")) is int and ctx["world_tick"] >= 0 and ctx.get("clock_mode") in ("FROZEN", "PARTIAL", "REALTIME")


def plan_synthetic(fixture: dict) -> dict:
    """Return a pure, deterministic scoped *proposal*, never a social or engine effect."""
    if not isinstance(fixture, dict) or fixture.get("source_kind") != "SYNTHETIC_TEST":
        return _out("QUARANTINED", "NOT_SYNTHETIC_FIXTURE")
    try:
        ctx = fixture["context"]
        req = fixture["request"]
        policy = fixture["trusted_policy"]
        proof = fixture["trusted_correction_registry"]
        subject = fixture["trusted_subject_registry"]
        case = fixture["trusted_case_registry"]
        exposure = fixture["trusted_exposure_ledger"]
        delivery = fixture["trusted_correction_delivery"]
        belief = fixture["trusted_belief_ledger"]
        rep = fixture["trusted_reputation_context"]
        harm = fixture["trusted_harm_ledger"]
        ledger = fixture["trusted_rehabilitation_ledger"]
        if not _valid_scope(ctx) or not isinstance(req, dict) or set(req) - _ALLOWED_REQUEST:
            return _out("QUARANTINED", "INVALID_CONTEXT_OR_REQUEST")
        if not all(isinstance(x, dict) for x in (policy, proof, subject, case, exposure, delivery, belief, rep, harm, ledger)):
            return _out("QUARANTINED", "INVALID_REGISTRY_SHAPE")
        if not all(_scope_matches(s, ctx) for s in (proof, subject, case, exposure, delivery, belief, rep, harm, ledger)):
            return _out("QUARANTINED", "CROSS_SCOPE_OR_STALE_AUTHORITY")
        types = ((proof, "CORRECTION_PROOF"), (subject, "SUBJECT_REGISTRY"),
                 (case, "REHABILITATION_CASE"), (exposure, "EXPOSURE_LEDGER"),
                 (delivery, "CORRECTION_DELIVERY"), (belief, "BELIEF_LEDGER"),
                 (rep, "REPUTATION_CONTEXT"), (harm, "HARM_LEDGER"), (ledger, "REHABILITATION_LEDGER"))
        if policy.get("trusted_kind") != "SYNTHETIC_SIGNED_POLICY" or \
           any(s.get("trusted_kind") != "SYNTHETIC_"+name or s.get("authenticated_fixture") is not True for s,name in types):
            return _out("QUARANTINED", "TRUSTED_FIXTURE_ATTESTATION_MISSING")
        if not isinstance(policy.get("revision"),str) or not policy["revision"].startswith("SYN-"):
            return _out("QUARANTINED", "POLICY_NOT_PINNED")
        if ctx.get("authenticated_principal") not in policy.get("authorized_principals", ()):
            return _out("DENIED", "PRINCIPAL_NOT_AUTHORIZED")
        if req.get("audience") not in policy.get("allowed_audiences", ()) or \
           req.get("purpose") not in policy.get("allowed_purposes", ()):
            return _out("DENIED", "PURPOSE_OR_AUDIENCE_NOT_AUTHORIZED")
        for key in ("case_ref", "subject_ref"):
            if not isinstance(req.get(key),str) or not req[key].startswith("SYN-"):
                return _out("QUARANTINED", "INVALID_REQUEST_REFERENCE")
        if req["case_ref"] != case.get("case_id") or req["subject_ref"] != subject.get("subject_id"):
            return _out("UNKNOWN", "CASE_OR_SUBJECT_NOT_FOUND")
        if case.get("subject_id") != subject.get("subject_id") or \
           proof.get("subject_id") != subject.get("subject_id") or \
           case.get("correction_ref") != proof.get("correction_id"):
            return _out("QUARANTINED", "CASE_PROOF_SUBJECT_MISMATCH")
        if req.get("expected_revision") != ledger.get("revision") or type(ledger.get("revision")) is not int:
            return _out("QUARANTINED", "STALE_LEDGER_REVISION")
        if case.get("status") != "OPEN" or case.get("consent_status") != "GRANTED" or \
           case.get("authorized_principal") != ctx["authenticated_principal"] or \
           case.get("purpose") != req["purpose"] or req["audience"] not in case.get("authorized_audiences", ()):
            return _out("DENIED", "CASE_CONSENT_OR_AUTHORIZATION_MISSING")
        if subject.get("kind") not in ("NPC", "FAC", "ORG", "PC") or \
           subject.get("owner_attested") is not True:
            return _out("QUARANTINED", "UNKNOWN_SUBJECT_OWNER")
        if subject["kind"] == "PC" and case.get("pc_owner_consent") is not True:
            return _out("DENIED", "PC_OWNER_CONSENT_REQUIRED")
        if proof.get("status") != "COMMITTED" or proof.get("source") != "DEC104_CURATED_CORRECTION" or \
           proof.get("grade") != "CORROBORATED" or not isinstance(proof.get("revision"),str) or \
           not proof.get("claim_ref") or not proof.get("source_family"):
            return _out("QUARANTINED", "PROOF_NOT_COMMITTED_OR_UNSUPPORTED")
        if type(proof.get("committed_at_tick")) is not int or proof["committed_at_tick"] > ctx["world_tick"]:
            return _out("QUARANTINED", "INVALID_CORRECTION_TIME")
        if proof.get("classification") not in _CLASSIFICATION or \
           type(subject.get("clearance")) is not int or subject["clearance"] < _CLASSIFICATION[proof["classification"]] or \
           req["audience"] not in subject.get("allowed_audiences", ()) or \
           req["purpose"] not in subject.get("allowed_purposes", ()):
            return _out("DENIED", "CLASSIFICATION_OR_SUBJECT_ACL_DENIED")
        if rep.get("subject_id") != subject["subject_id"] or rep.get("dimension") not in policy.get("allowed_dimensions", ()) or \
           rep.get("audience") != req["audience"] or rep.get("revision",-1)<0:
            return _out("QUARANTINED", "REPUTATION_CONTEXT_NOT_PINNED")
        if case.get("reputation_context_id") != rep.get("context_id") or not rep.get("owner_attested"):
            return _out("QUARANTINED", "REPUTATION_OWNER_MISMATCH")
        if exposure.get("claim_ref") != proof["claim_ref"] or exposure.get("subject_id") != subject["subject_id"]:
            return _out("QUARANTINED", "ACCUSATION_EXPOSURE_NOT_GROUNDED")
        if exposure.get("state") not in ("NOT_OBSERVED", "PERCEIVED") or \
           type(exposure.get("heard_at_tick")) is not int or exposure["heard_at_tick"]>ctx["world_tick"]:
            return _out("QUARANTINED", "EXPOSURE_LEDGER_INVALID")
        if delivery.get("correction_id") != proof["correction_id"] or delivery.get("revision") != proof["revision"] or \
           delivery.get("audience") != req["audience"] or delivery.get("state") not in _DELIVERY:
            return _out("QUARANTINED", "CORRECTION_DELIVERY_NOT_GROUNDED")
        if delivery.get("state") == "UNCERTAIN":
            return _out("QUARANTINED", "UNCERTAIN_DELIVERY_REQUIRES_RECONCILIATION")
        if delivery.get("state") == "DELIVERED":
            if type(delivery.get("arrived_at_tick")) is not int or not (proof["committed_at_tick"] <= delivery["arrived_at_tick"] <= ctx["world_tick"]):
                return _out("QUARANTINED", "INVALID_DELIVERY_TIME")
        if belief.get("subject_context_id") != rep["context_id"] or \
           belief.get("state") not in _BELIEFS or belief.get("trust_state") not in _TRUST:
            return _out("QUARANTINED", "INVALID_BELIEF_OR_TRUST_CONTEXT")
        if harm.get("subject_id") != subject["subject_id"] or harm.get("claim_ref") != proof["claim_ref"] or \
           harm.get("state") not in _DAMAGE:
            return _out("QUARANTINED", "HARM_CAUSAL_LINK_INVALID")
        if harm["state"] == "HOST_CONFIRMED" and (not isinstance(harm.get("host_receipt_ref"),str) or not harm["host_receipt_ref"].startswith("SYN-")):
            return _out("QUARANTINED", "HARM_HOST_RECEIPT_MISSING")
        if case.get("high_risk_unresolved") is True or rep.get("high_risk_unresolved") is True:
            return _out("QUARANTINED", "HIGH_RISK_GATE_UNRESOLVED")
        case_key = _hash(tuple(ctx[k] for k in _SCOPE), policy["revision"],
                         case["case_id"], proof["revision"], rep["context_id"],
                         rep["revision"], ledger["revision"])
        if case_key in ledger.get("committed_case_keys", ()):
            return _out("ALREADY_REGISTERED", "REHABILITATION_CASE_ALREADY_REGISTERED", case_key=case_key)
        if case_key in ledger.get("pending_case_keys", ()):
            return _out("ALREADY_PLANNED", "REHABILITATION_CASE_ALREADY_PROPOSED", case_key=case_key)
        if exposure["state"] != "PERCEIVED":
            return _out("NO_REPUTATIONAL_EXPOSURE", "ORIGINAL_ACCUSATION_NOT_PROVEN_HEARD", case_key=case_key)
        if delivery["state"] != "DELIVERED":
            action = "PROPOSE_SCOPED_CORRECTION_NOTICE"
        elif delivery.get("perception") != "CONFIRMED":
            action = "WAIT_FOR_CORRECTION_PERCEPTION"
        elif belief["state"] != "REVISED":
            action = "PROPOSE_OPTIONAL_TRUST_DIALOGUE"
        elif belief["trust_state"] in ("BROKEN", "CONTESTED", "UNREVIEWED", "UNCHANGED"):
            action = "PROPOSE_VOLUNTARY_REENGAGEMENT"
        else:
            action = "NO_FORCED_ADDITIONAL_TRUST_CHANGE"
        remedy = "REFER_TO_SEPARATE_RESTITUTION_REVIEW" if harm["state"] == "HOST_CONFIRMED" else \
                 "REQUEST_EVIDENCE_FOR_HARM" if harm["state"] in ("ALLEGED", "CORROBORATED", "DISPUTED") else \
                 "NO_MATERIAL_RESTITUTION_CLAIM"
        return _out("PROPOSAL_READY", "CONTEXTUAL_REHABILITATION_ELIGIBLE", case_key=case_key,
                    proposed_social_action=action, suggested_harm_next_step=remedy,
                    scope_dimension=rep["dimension"],
                    caveat="PROPOSAL_ONLY;NO_AUTO_REPUTATION_RESTORE;NO_FORCED_FORGIVENESS")
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        # No user-controlled payload or secret included in errors.
        return _out("QUARANTINED", "INVALID_OR_INCOMPLETE_SYNTHETIC_CONTRACT")
