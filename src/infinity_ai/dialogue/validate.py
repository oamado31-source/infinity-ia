# SPDX-License-Identifier: Apache-2.0
"""SPEC-004 output validation (ADR-0055 style, low-risk tier: NPC flavour speech).

Heuristic gates on the model's JSON reply. They catch the detectable failures (made-up fact ids,
leaked codes or internals, names that are nowhere in the NPC's context, broken format); they do
not prove each sentence is true. A reply that fails is retried once, then replaced by a fallback.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .context import DialogueContext

MAX_SPEECH = 400
_CODES = re.compile(r'\b[A-Z]{2}\d{3,4}\b|\b(?:ev|xp|rev|br)-[0-9a-f]{6,}|\bnpc:\w+|\bsha256:', re.I)
_META = re.compile(r'modelo de linguagem|intelig[eê]ncia artificial|\bprompt\b|\bsistema\b'
                   r'|language model|\bas an ai\b|\b[FK]\d+\b|used_facts', re.I)
_META_EXACT = re.compile(r'\bIA\b|\bAI\b')  # case-sensitive: "eu ia" is ordinary Portuguese
_MARKUP = re.compile(r'[<>{}\[\]`*#|]')
# First-person claims of ownership, rank or kin (ADR-0117 rule 8): only allowed when the
# person's own FATOS say so.
_SELF_CLAIM = re.compile(
    r'\b(?:me pertence|me pertencem|(?:sou|eu sou) (?:o|a) (?:dono|dona|senhor|senhora|chefe|'
    r'líder|rei|rainha|lorde|capitão|capitã|governante)|(?:meu|minha|meus|minhas) '
    r'(?:pai|mãe|irmão|irmã|filho|filha|esposa|marido|família|terras|propriedades))\b', re.I)
_WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'-]*")
_BOUNDARY = re.compile(r'[.!?…:"“«—]')


@dataclass(frozen=True)
class Verdict:
    ok: bool
    reasons: tuple[str, ...]
    speech: str
    used_facts: tuple[str, ...]
    unknown: bool


def _unknown_names(speech: str, vocabulary: frozenset[str]) -> list[str]:
    """Capitalised words that are not sentence-initial and not in the context vocabulary."""
    allowed = {w.lower() for w in vocabulary}
    found, prev_end = [], 0
    for match in _WORD.finditer(speech):
        sentence_start = prev_end == 0 or bool(_BOUNDARY.search(speech[prev_end:match.start()]))
        word = match.group(0)
        if word[0].isupper() and not sentence_start and word.lower() not in allowed:
            found.append(word)
        prev_end = match.end()
    return found


def player_names(player_text: str | None) -> frozenset[str]:
    """Capitalised words the player wrote (an NPC may echo them only while admitting ignorance)."""
    if not player_text:
        return frozenset()
    return frozenset(w for w in _WORD.findall(player_text) if w[0].isupper())


def validate_reply(raw: str, context: DialogueContext, player_text: str | None = None) -> Verdict:
    reasons: list[str] = []
    try:
        doc = json.loads(raw)
    except (TypeError, ValueError):
        return Verdict(False, ('NOT_JSON',), '', (), False)
    if not isinstance(doc, dict):
        return Verdict(False, ('NOT_OBJECT',), '', (), False)
    speech, used, unknown = doc.get('speech'), doc.get('used_facts'), doc.get('unknown')
    if not isinstance(speech, str) or not isinstance(used, list) or not isinstance(unknown, bool) \
            or not all(isinstance(u, str) for u in used):
        return Verdict(False, ('BAD_SHAPE',), '', (), False)
    speech = ' '.join(speech.split())
    if not speech:
        reasons.append('EMPTY')
    if len(speech) > MAX_SPEECH:
        reasons.append('TOO_LONG')
    known_ids = {f.fact_id for f in context.facts + context.knowledge + context.restricted_knowledge}
    invented = sorted(set(used) - known_ids)
    if invented:
        reasons.append('UNKNOWN_FACT_IDS:' + ','.join(invented))
    if _CODES.search(speech):
        reasons.append('RAW_CODE')
    if _META.search(speech) or _META_EXACT.search(speech):
        reasons.append('META_TALK')
    if _MARKUP.search(speech):
        reasons.append('MARKUP')
    claim = _SELF_CLAIM.search(speech)
    if claim:
        # The claimed word (dono, lorde, pai, ...) must be in the person's facts or own name.
        word = claim.group(0).split()[-1].lower()
        own_facts = [f.text for f in context.facts]
        own_facts += [f.text for f in context.knowledge + context.restricted_knowledge
                      if f.subject_id == context.persona.npc_id]
        own = ' '.join(own_facts + [context.persona.display_name]).lower()
        if word not in own:
            reasons.append('SELF_CLAIM')
    vocabulary = context.vocabulary | (player_names(player_text) if unknown else frozenset())
    names = _unknown_names(speech, vocabulary)
    if names:
        reasons.append('UNKNOWN_NAMES:' + ','.join(sorted(set(names))))
    return Verdict(not reasons, tuple(reasons), speech, tuple(dict.fromkeys(used)), unknown)
