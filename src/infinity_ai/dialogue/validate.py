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
# ADR-0120: claims about where the person is from, checked against its standing and facts.
_AWAY_CLAIM = re.compile(
    r'\b(?:não sou (?:daqui|de aqui|de cá|desta cidade)|estou de passagem|sou de fora|'
    r'sou (?:um |uma )?(?:forasteir[oa]|estrangeir[oa]|viajante))\b', re.I)
_HOME_CLAIM = re.compile(r'(?<!não )\b(?:sou (?:daqui|de aqui|de cá)|moro aqui|vivo aqui)\b',
                         re.I)
# Working at the place where one is: only with a curated STAFF affiliation (ADR-0119/0120).
_WORK_CLAIM = re.compile(
    r'(?<!não )\b(?:trabalho (?:aqui|nesta casa|nesta taverna|na taverna|na casa|para o dono|'
    r'para (?:ele|ela) aqui)|sou (?:funcionári[oa]|empregad[oa]) (?:daqui|da casa|desta casa|'
    r'da taverna|desta taverna))\b', re.I)
_BORN_CLAIM = re.compile(r'(?<!não )\b(?:nasci|cresci) aqui\b', re.I)
_ORIGIN_CLAIM = re.compile(
    r"\b(?i:sou de|vim de|venho de|nasci em|sou natural de)\s+(?:[ao]s? )?"
    r"([A-ZÀ-Ý][\w'-]+)")
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


def _origin_contradicts(speech: str, context: DialogueContext) -> str | None:
    """ADR-0120: which claim about where the person is from contradicts its standing or facts
    ("não sou daqui" from a resident, "moro aqui" from a traveler, "nasci aqui" or "vim de X"
    not in its facts, "trabalho aqui" without a STAFF tie), or None."""
    resident = context.standing == 'HABITANTE'
    facts = ' '.join(f.text for f in context.facts).lower()
    if _AWAY_CLAIM.search(speech) and resident:
        return 'AWAY'
    if _HOME_CLAIM.search(speech) and not resident:
        return 'HOME'
    if _BORN_CLAIM.search(speech) and 'nasceu' not in facts:
        return 'BORN'
    if _WORK_CLAIM.search(speech) and not context.staff:
        return 'WORK'
    if any(m.group(1).lower() not in facts for m in _ORIGIN_CLAIM.finditer(speech)):
        return 'ORIGIN'
    return None


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
    why = _origin_contradicts(speech, context) if context.standing else None
    if why:
        reasons.append(f'SELF_CLAIM:{why}')      # the log shows which claim was refused
    vocabulary = context.vocabulary | (player_names(player_text) if unknown else frozenset())
    names = _unknown_names(speech, vocabulary)
    if names:
        reasons.append('UNKNOWN_NAMES:' + ','.join(sorted(set(names))))
    return Verdict(not reasons, tuple(reasons), speech, tuple(dict.fromkeys(used)), unknown)
