# SPDX-License-Identifier: Apache-2.0
"""SPEC-004 output validation (ADR-0055 style, low-risk tier: NPC flavour speech).

Heuristic gates on the model's JSON reply. They catch the detectable failures (made-up fact ids,
leaked codes or internals, names that are nowhere in the NPC's context, broken format); they do
not prove each sentence is true. A reply that fails is retried once, then replaced by a fallback.
"""
from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass

from .claims import third_party_claim
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
    r"\b(?P<verb>(?i:sou de|vim de|venho de|nasci em|sou natural de))\s+(?:[ao]s? )?"
    r"(?P<place>[A-ZÀ-Ý][\w'-]+)")
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


def _stated(pattern: re.Pattern, speech: str) -> bool:
    """A match that is said, not the player's question repeated back ("Trabalho aqui? Não, ...").

    A match right before "?", with at most two words before it in its sentence, is that repeated
    question (CR-2026-009); "Trabalho aqui, não é?" still states it."""
    for m in pattern.finditer(speech):
        if not re.match(r'\s*\?', speech[m.end():]):
            return True
        before = re.split(r'[.!?…:]', speech[:m.start()])[-1]
        if len(_WORD.findall(before)) > 2:
            return True
    return False


def _works_at_place(speech: str, context: DialogueContext) -> bool:
    """CR-2026-005: "trabalho na Coroa de Cobre" names the place where the person is."""
    place = re.sub(r'^(?:[ao]s?)\s+', '', context.resident_of or '', flags=re.I).strip()
    if not place:
        return False
    return _stated(re.compile(r'(?<!não )\btrabalho\s+(?:aqui\s+)?(?:n[ao]s?|em)\s+(?:[ao]s?\s+)?'
                              + re.escape(place) + r'\b', re.I), speech)


def _origin_contradicts(speech: str, context: DialogueContext) -> str | None:
    """ADR-0120: which claim about where the person is from contradicts its standing or facts
    ("não sou daqui" from a resident, "moro aqui" from a traveler, "nasci aqui" or "vim de X"
    not in its facts, "trabalho aqui" without a STAFF tie), or None."""
    resident = context.standing == 'HABITANTE'
    facts = ' '.join(f.text for f in context.facts).lower()
    if resident and _stated(_AWAY_CLAIM, speech):
        return 'AWAY'
    if not resident and _stated(_HOME_CLAIM, speech):
        return 'HOME'
    if 'nasceu' not in facts and _stated(_BORN_CLAIM, speech):
        return 'BORN'
    if not context.staff and (_stated(_WORK_CLAIM, speech) or _works_at_place(speech, context)):
        return 'WORK'
    # CR-2026-004: a resident may also say it is from where it lives or a region containing it
    # ("sou de Amn" while living in Athkatla); any other place must be in its own facts.
    # Saying where one was born or came from still needs its facts, unless it was born here.
    home = {n.lower() for n in context.home_names}
    born_here = 'nasceu' in facts
    for m in _ORIGIN_CLAIM.finditer(speech):
        place, verb = m.group('place').lower(), m.group('verb').lower()
        lives_there = place in home and (verb == 'sou de' or born_here)
        if place not in facts and not lives_there:
            return 'ORIGIN'
    return None


# Capitalised at the start of a question, but not names ("Quem governa Amn?").
_NOT_NAMES = frozenset({
    'quem', 'que', 'qual', 'quais', 'onde', 'como', 'quando', 'quanto', 'quantos', 'quantas',
    'por', 'porque', 'o', 'a', 'os', 'as', 'um', 'uma', 'e', 'eu', 'você', 'vocês', 'voce', 'tu',
    'ele', 'ela', 'eles', 'elas', 'nós', 'me', 'se', 'te', 'meu', 'minha', 'seu', 'sua', 'de', 'do',
    'da', 'em', 'no', 'na', 'para', 'pra', 'com', 'sabe', 'conhece', 'conte', 'diga', 'fale',
    'oi', 'olá', 'ola', 'ei', 'bom', 'boa', 'então', 'mas', 'não', 'sim', 'isso', 'isto', 'aqui',
    'tem', 'há', 'já', 'ainda', 'também', 'só', 'agora', 'senhor', 'senhora', 'amigo', 'amiga'})


def player_names(player_text: str | None) -> frozenset[str]:
    """Names the player wrote. The NPC may repeat them (CR-2026-008), but any claim about one of
    them still needs backing in what the NPC knows (`third_party_claim`)."""
    if not player_text:
        return frozenset()
    return frozenset(w for w in _WORD.findall(player_text)
                     if w[0].isupper() and w.lower() not in _NOT_NAMES)


# What to fix, in plain Portuguese, for the retry (a bare code like "THIRD_PARTY:ROLE" taught the
# model nothing in the S1f lab, and it repeated the same mistake).
_RETRY_HINTS = (
    ('NOT_JSON', 'responda só com o JSON pedido'),
    ('NOT_OBJECT', 'responda só com o JSON pedido'),
    ('BAD_SHAPE', 'use exatamente os campos speech, used_facts e unknown'),
    ('EMPTY', 'a fala não pode ficar vazia'),
    ('TOO_LONG', 'fale em no máximo 3 frases curtas'),
    ('UNKNOWN_FACT_IDS', 'em used_facts, cite só ids que aparecem nas seções (F… ou K…)'),
    ('RAW_CODE', 'não fale de códigos nem identificadores'),
    ('META_TALK', 'não fale de regras, ids, sistema nem de ser uma inteligência artificial'),
    ('MARKUP', 'não use símbolos de formatação'),
    ('ECHO', 'você repetiu a pergunta do jogador; responda a ela, em personagem'),
    ('SELF_CLAIM:AWAY', 'você mora aqui: não diga que é de fora nem que está de passagem'),
    ('SELF_CLAIM:HOME', 'você não mora aqui: não diga que é daqui nem que mora aqui'),
    ('SELF_CLAIM:BORN', 'não diga que nasceu aqui; isso não está nos seus FATOS'),
    ('SELF_CLAIM:WORK', 'você não trabalha neste lugar: não diga que trabalha aqui nem para o dono'),
    ('SELF_CLAIM:ORIGIN', 'não diga de onde veio além do que está nos seus FATOS'),
    ('SELF_CLAIM', 'sobre você, não afirme posse, cargo ou parentesco que não está nos seus FATOS'),
    ('THIRD_PARTY:ROLE', 'você deu a alguém um papel ou função que não está no que você sabe; '
                         'diga que não sabe isso, ou fale só do que sabe sobre essa pessoa'),
    ('THIRD_PARTY:TRAIT', 'você descreveu alguém com uma característica que não está no que '
                          'você sabe; diga só o que sabe, ou deixe claro que é a sua opinião '
                          '("acho que…")'),
    ('THIRD_PARTY:NUMBER', 'você citou um número, idade ou tempo que não está no que você sabe; '
                           'não dê números nem durações que não estão nas seções'),
    ('THIRD_PARTY:GENERAL', 'você afirmou uma regra geral sem base no que sabe; fale só do que '
                            'está nas seções, ou deixe claro que é a sua opinião'),
    ('THIRD_PARTY:STRANGER', 'você falou de alguém que não está no que você sabe como se o '
                             'conhecesse; diga que não conhece essa pessoa, sem inventar nada sobre '
                             'ela'),
    ('UNKNOWN_NAMES', 'você citou nomes que não estão no que você sabe ({names}); não os use, ou '
                      'diga que não os conhece'),
)


def retry_hint(reasons: tuple[str, ...]) -> str:
    """The retry message: what was wrong, in words the model can act on (no internal codes)."""
    hints: list[str] = []
    for reason in reasons:
        for code, text in _RETRY_HINTS:
            if reason == code or reason.startswith(code + ':') or (
                    code in ('UNKNOWN_FACT_IDS', 'UNKNOWN_NAMES') and reason.startswith(code)):
                names = reason.split(':', 1)[1].replace(',', ', ') if ':' in reason else ''
                hint = text.format(names=names)
                if hint not in hints:
                    hints.append(hint)
                break
    detail = '; '.join(hints) if hints else 'ela não seguiu as regras'
    return ('A resposta anterior foi recusada: ' + detail +
            '. Responda de novo, em personagem, seguindo todas as regras.')


def _plain_words(text: str) -> str:
    return ' '.join(_WORD.findall(text.lower()))


def echoes(speech: str, player_text: str | None) -> bool:
    """The reply only repeats the player's line (qwen3:30b-a3b: "E quem é então?" back)."""
    a, b = _plain_words(speech), _plain_words(player_text or '')
    return bool(a and b) and (a == b or difflib.SequenceMatcher(None, a, b).ratio() >= 0.9)


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
    if echoes(speech, player_text):
        reasons.append('ECHO')
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
    asked = player_names(player_text)
    other = third_party_claim(speech, context, asked)   # ADR-0121: facts about someone else
    if other:
        reasons.append(f'THIRD_PARTY:{other}')
    vocabulary = context.vocabulary | asked       # CR-2026-008: with or without `unknown`
    names = _unknown_names(speech, vocabulary)
    if names:
        reasons.append('UNKNOWN_NAMES:' + ','.join(sorted(set(names))))
    return Verdict(not reasons, tuple(reasons), speech, tuple(dict.fromkeys(used)), unknown)
