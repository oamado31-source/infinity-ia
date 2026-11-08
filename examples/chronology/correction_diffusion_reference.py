"""DEC-105/C: SYNTHETIC-ONLY, pure deterministic correction & belief-review proposal.
No BG2:EE, EEex, host, messaging, LLM or persisted memory access. All trusted stores
are grouped in the fixture solely to exercise the proposed authorization boundaries.
"""
from __future__ import annotations
import hashlib
import json

_SCOPE = ("campaign_id", "branch_id", "lineage_id", "build_fingerprint", "modpack_hash", "host_epoch", "checkpoint_epoch")
_STATES = frozenset(("PENDING", "IN_TRANSIT", "LOST", "DELIVERED", "UNCERTAIN"))
_LEVELS = {"PUBLIC": 0, "RESTRICTED": 1, "PROTECTED": 2}
_EVIDENCE = frozenset(("UNVERIFIED", "CONTESTED", "PARTIAL", "CORROBORATED"))
_BELIEFS = frozenset(("NEVER_HEARD", "HEARD_UNASSESSED", "BELIEVES_PRIOR", "DOUBTS_PRIOR", "CONTESTED", "REVISED"))


def _out(status, reason, **kwargs):
    return dict(status=status, reason=reason, host_calls=0, engine_writes=0,
                deliveries_sent=0, npc_memories_changed=0,
                npc_beliefs_committed=0, ledger_mutated=False, **kwargs)


def _key(*parts):
    blob=json.dumps(parts, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _scope_valid(record, ctx):
    return isinstance(record, dict) and all(record.get(k) == ctx.get(k) for k in _SCOPE)


def plan_synthetic(fixture):
    """Compute only a deterministic proposal. Never commit, send or update beliefs.

    The registry/policy/ledger/receipts MUST be authenticated and independent in any
    future implementation; these fixture dictionaries are NOT client input to trust.
    """
    if not isinstance(fixture, dict) or fixture.get("source_kind") != "SYNTHETIC_TEST":
        return _out("QUARANTINED", "NOT_SYNTHETIC_FIXTURE")
    try:
        ctx=fixture["context"]; request=fixture["request"]
        policy=fixture["trusted_policy"]; registry=fixture["trusted_correction_registry"]
        recipient=fixture["trusted_recipient_registry"]; channel=fixture["trusted_channel_ledger"]
        beliefs=fixture["trusted_belief_ledger"]
    except (KeyError, TypeError):
        return _out("QUARANTINED", "MISSING_AUTHORITY")
    if not isinstance(ctx, dict) or not isinstance(request, dict) or \
       ctx.get("fixture_only") is not True or ctx.get("host_mode") != "SYNTHETIC_HOST_FIXTURE":
        return _out("QUARANTINED", "INVALID_CONTEXT")
    if any(k not in ctx for k in _SCOPE) or any(not isinstance(ctx[k], (str, int)) or isinstance(ctx[k], bool) for k in _SCOPE):
        return _out("QUARANTINED", "INVALID_SCOPE")
    if any(not isinstance(ctx[k], str) or not ctx[k].startswith("SYN-") for k in _SCOPE[:5]):
        return _out("QUARANTINED", "NOT_SYNTHETIC_SCOPE")
    if any(type(ctx[k]) is not int or ctx[k]<0 for k in _SCOPE[5:]):
        return _out("QUARANTINED", "INVALID_EPOCH")
    now=ctx.get("world_tick")
    if type(now) is not int or now<0 or ctx.get("clock_mode") not in ("FROZEN", "PARTIAL", "REALTIME"):
        return _out("QUARANTINED", "INVALID_WORLD_CLOCK")
    if not all(isinstance(s,dict) for s in (policy,registry,recipient,channel,beliefs)):
        return _out("QUARANTINED", "INVALID_TRUSTED_STORE_SHAPE")
    if ctx.get("authenticated_principal") not in policy.get("authorized_principals",()):
        return _out("DENIED", "PRINCIPAL_NOT_AUTHORIZED")
    if not all(_scope_valid(s,ctx) for s in (registry,recipient,channel,beliefs)):
        return _out("QUARANTINED", "CROSS_SCOPE_OR_STALE_AUTHORITY")
    if policy.get("trusted_kind")!="SYNTHETIC_SIGNED_POLICY" or \
       not all(s.get("trusted_kind")==expected and s.get("authenticated_fixture") is True for s,expected in (
           (registry,"SYNTHETIC_CORRECTION_REGISTRY"),(recipient,"SYNTHETIC_RECIPIENT_REGISTRY"),
           (channel,"SYNTHETIC_DELIVERY_LEDGER"),(beliefs,"SYNTHETIC_BELIEF_LEDGER"))):
        return _out("QUARANTINED", "UNTRUSTED_STORES")
    if not isinstance(request.get("recipient_ref"),str) or not request.get("recipient_ref", "").startswith("SYN-") or \
       not isinstance(request.get("correction_ref"),str) or not request.get("correction_ref", "").startswith("SYN-"):
        return _out("QUARANTINED", "INVALID_REQUEST_REFERENCE")
    if request.get("correction_ref")!=registry.get("correction_id"):
        return _out("UNKNOWN", "CORRECTION_NOT_FOUND")
    if request.get("recipient_ref")!=recipient.get("recipient_id") or request["recipient_ref"]!=beliefs.get("recipient_id"):
        return _out("UNKNOWN", "RECIPIENT_NOT_FOUND")
    if request.get("purpose") not in policy.get("allowed_purposes",()) or \
       request.get("audience") not in policy.get("allowed_audiences",()):
        return _out("DENIED", "PURPOSE_OR_AUDIENCE_NOT_ALLOWED")
    if request.get("expected_ledger_revision")!=beliefs.get("revision") or type(beliefs.get("revision")) is not int:
        return _out("QUARANTINED", "STALE_BELIEF_LEDGER_REVISION")
    if not policy.get("revision") or not isinstance(policy["revision"], str):
        return _out("QUARANTINED", "POLICY_NOT_PINNED")
    if registry.get("status")!="COMMITTED" or registry.get("proof_source")!="DEC104_CURATED_PROOF" or \
       not registry.get("revision") or not registry.get("original_claim_ref"):
        return _out("QUARANTINED", "CORRECTION_NOT_COMMITTED")
    if type(registry.get("committed_at_tick")) is not int or registry["committed_at_tick"]>now:
        return _out("QUARANTINED", "CORRECTION_NOT_YET_COMMITTED_AT_DR_TICK")
    if registry.get("classification") not in _LEVELS or type(recipient.get("clearance")) is not int or \
       recipient["clearance"]<_LEVELS[registry["classification"]] or \
       request.get("audience") not in recipient.get("audiences",()):
        return _out("DENIED", "RECIPIENT_NOT_AUTHORIZED")
    if registry.get("purpose")!=request.get("purpose") or \
       request.get("purpose") not in recipient.get("allowed_purposes",()):
        return _out("DENIED", "RECIPIENT_PURPOSE_NOT_AUTHORIZED")
    if registry.get("evidence_grade") not in _EVIDENCE or \
       recipient.get("belief_before") not in _BELIEFS or beliefs.get("belief_before")!=recipient.get("belief_before"):
        return _out("QUARANTINED", "INVALID_EVIDENCE_OR_BELIEF_BASELINE")
    if registry.get("source_family") is None or not isinstance(registry["source_family"], str):
        return _out("QUARANTINED", "MISSING_PROVENANCE_FAMILY")
    if registry.get("revision") in beliefs.get("committed_revision_refs",()):
        return _out("ALREADY_REVIEWED", "COMMITTED_BELIEF_REVIEW_EXISTS")
    if request.get("delivery_ref")!=channel.get("delivery_id") or \
       request.get("recipient_ref")!=channel.get("recipient_id") or \
       registry.get("revision")!=channel.get("correction_revision") or \
       registry["correction_id"]!=channel.get("correction_id"):
        return _out("UNKNOWN", "DELIVERY_NOT_GROUNDED")
    if channel.get("state") not in _STATES:
        return _out("QUARANTINED", "INVALID_DELIVERY_STATE")
    if channel.get("channel") not in policy.get("allowed_channels",()) or \
       type(channel.get("hop_count")) is not int or type(policy.get("max_hops")) is not int or \
       not 0<=channel["hop_count"]<=policy["max_hops"]:
        return _out("DENIED", "CHANNEL_OR_HOP_NOT_ALLOWED")
    if type(channel.get("sent_at_tick")) is not int or type(channel.get("arrived_at_tick")) is not int or \
       channel["sent_at_tick"] < registry["committed_at_tick"] or \
       channel["arrived_at_tick"] < channel["sent_at_tick"]:
        return _out("QUARANTINED", "INVALID_DELIVERY_CHRONOLOGY")
    if channel["sent_at_tick"]>now:
        return _out("QUARANTINED", "FUTURE_SEND_NOT_ALLOWED")
    if channel["state"] in ("PENDING","IN_TRANSIT","LOST","UNCERTAIN"):
        return _out("DELIVERY_NOT_CONFIRMED", "TRANSMISSION_NOT_KNOWLEDGE")
    if channel["arrived_at_tick"]>now:
        return _out("QUARANTINED", "FUTURE_DELIVERY_NOT_ALLOWED")
    if channel.get("perception")!="CONFIRMED":
        return _out("DELIVERY_NOT_CONFIRMED", "RECEIPT_IS_NOT_PERCEPTION")
    case_key=_key(*(ctx[k] for k in _SCOPE), registry["correction_id"], registry["revision"],
                  recipient["recipient_id"], channel["delivery_id"], policy["revision"])
    if case_key in beliefs.get("planned_case_keys",()) or case_key in beliefs.get("pending_case_keys",()):
        return _out("DUPLICATE_SUPPRESSED", "REVIEW_ALREADY_SCHEDULED",case_key=case_key)
    if registry["evidence_grade"] in ("UNVERIFIED","CONTESTED"):
        next_step="HOLD_DISPUTED_CLAIM"
    elif recipient["belief_before"]=="NEVER_HEARD":
        next_step="RECORD_CORRECTION_WITHOUT_INFERRING_PRIOR_BELIEF"
    elif registry["evidence_grade"]=="PARTIAL":
        next_step="PROPOSE_PARTIAL_RECONSIDERATION"
    elif recipient.get("source_confidence") not in ("LOW","MEDIUM","HIGH"):
        return _out("QUARANTINED", "UNKNOWN_SOURCE_CONFIDENCE")
    elif recipient["source_confidence"]=="LOW":
        next_step="PROPOSE_CONTESTED_REVIEW"
    else:
        next_step="PROPOSE_EVIDENCE_BASED_RECONSIDERATION"
    return _out("BELIEF_REVIEW_PROPOSED", "AUTHORIZED_DELIVERY_FOR_CONTEXTUAL_REVIEW",
                case_key=case_key, proposed_action=next_step,
                evidence_grade=registry["evidence_grade"],
                prior_belief=recipient["belief_before"],
                caveat="PROPOSAL_ONLY;NO_AUTOMATIC_ACCEPTANCE_OR_MEMORY_REWRITE")
