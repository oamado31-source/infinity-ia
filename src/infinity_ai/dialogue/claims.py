# SPDX-License-Identifier: Apache-2.0
"""ADR-0121: what an NPC states about someone else must be in what it knows about them.

An opinion of the speaker passes ("Cruel!", "acho que ele é duro", "não confio nele"), except
for numbers and durations, which need the knowledge even when hedged (CR-2026-006); what is
stated as a fact about another person or group does not, unless the speaker's own context says
it: a role ("o taverneiro é Lehtinan"), a trait ("Lehtinan? Cara duro", or a later clause with
the subject left out: "Lehtinan? Dono da taverna. Não fala muito"), a number or a duration
("governam há décadas", "vivo aqui há 20 anos") or a general rule ("governa quem tem dinheiro").

Local Portuguese patterns, checked against the context texts that mention the name, with a small
curated synonym table (our own words). Pronouns ("ele é o dono") are not resolved, and
paraphrases outside these patterns are not caught: this narrows invention, it does not prove
truth.
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from .context import DialogueContext

# Synonym groups: a claim word is backed when any word of its group appears (written by us).
_GROUPS = (
    ('dono', 'dona', 'donos', 'proprietário', 'proprietária'),
    ('taverneiro', 'taverneira', 'taberneiro', 'gerente', 'administrador', 'administradora',
     'administra', 'cuida', 'coordena'),
    ('conselheiro', 'conselheira', 'conselheiros', 'conselho'),
    ('governante', 'governantes', 'governa', 'governam', 'governo'),
    ('chefe', 'líder', 'lidera', 'comanda'),
    ('guarda', 'guardas', 'vigia'),
    ('dinheiro', 'ouro', 'riqueza', 'rico', 'rica', 'ricos', 'ricas', 'moedas'),
    ('poder', 'poderoso', 'poderosa', 'poderosos'),
)
SYNONYMS: dict[str, tuple[str, ...]] = {w: group for group in _GROUPS for w in group}

ROLE_WORDS = frozenset({
    'dono', 'dona', 'proprietário', 'proprietária', 'taverneiro', 'taverneira', 'taberneiro',
    'gerente', 'administrador', 'administradora', 'guarda', 'capitão', 'capitã', 'chefe',
    'líder', 'conselheiro', 'conselheira', 'governante', 'rei', 'rainha', 'senhor', 'senhora',
    'patrão', 'patroa', 'sócio', 'sócia', 'pai', 'mãe', 'irmão', 'irmã', 'filho', 'filha',
    'esposa', 'marido'})
_FILLER = frozenset({
    'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das', 'que', 'quem', 'muito',
    'muita', 'bem', 'mais', 'meio', 'bastante', 'tão', 'aqui', 'lá', 'daqui', 'sim', 'não', 'só',
    'e', 'mas', 'também', 'sempre', 'ainda', 'cara', 'homem', 'mulher', 'sujeito', 'sujeita',
    'tipo', 'pessoa', 'velho', 'velha', 'gente', 'em', 'no', 'na', 'por', 'pra', 'para', 'com'})
_NUMBER_WORDS = {'uma': '1', 'um': '1', 'duas': '2', 'dois': '2', 'três': '3', 'quatro': '4',
                 'cinco': '5', 'seis': '6', 'sete': '7', 'oito': '8', 'nove': '9', 'dez': '10',
                 'vinte': '20', 'trinta': '30', 'quarenta': '40', 'cinquenta': '50', 'cem': '100'}
_UNITS = ('década', 'ano', 'século', 'mes')

_CAP = r"[A-ZÀ-Ý][\wÀ-ÿ'-]+"
_LOW = r"[a-zà-ÿ][\wà-ÿ-]*"
_ROLE_PATTERNS = (
    re.compile(rf"(?P<name>{_CAP})\s*,?\s+(?i:é|era)\s+(?i:o\s+|a\s+|um\s+|uma\s+)?(?P<role>{_LOW})"),
    re.compile(rf"\b(?i:o|a)\s+(?P<role>{_LOW})(?:\s+(?i:daqui|da casa|desta casa|da taverna|"
               rf"dessa taverna|desta taverna|do lugar|do local|deste lugar))?\s+(?i:é|era)\s+"
               rf"(?i:o\s+|a\s+)?(?P<name>{_CAP})"),
    re.compile(rf"(?P<name>{_CAP}),\s+(?i:o|a)\s+(?P<role>{_LOW})"),
)
# Someone the player named and the speaker knows nothing about: any "X é o/um <noun>" is a claim,
# not only the role words above ("Gorion? É o mago da fortaleza.").
_STRANGER_ROLE = (
    re.compile(rf"(?P<name>{_CAP})\s*,?\s+(?i:é|era)\s+(?i:o|a|um|uma)\s+(?P<role>{_LOW})"),
    re.compile(rf"(?P<name>{_CAP}),\s+(?i:o|a|um|uma)\s+(?P<role>{_LOW})"),
    re.compile(rf"(?P<name>{_CAP})\s*[?:!.…]\s*(?i:é|era)\s+(?i:o|a|um|uma)\s+(?P<role>{_LOW})"),
)
_NOT_A_ROLE = frozenset({'nome', 'que', 'quem', 'qual', 'mistério'})
# A stranger may be named only while saying one does not know them, sending the player to someone
# else, refusing to talk, or giving an opinion; "Ah, o Galê está na taverna." is invented.
_IGNORANCE = re.compile(
    r"\b(?:não sei|sei lá|nunca ouvi|não ouvi|nunca vi|não vi|não conheço|nunca conheci|"
    r"desconheço|não faço (?:a menor )?ideia|não tenho (?:a menor )?ideia|não lembro|"
    r"não me lembro|ninguém sabe|ninguém conhece|não sei dizer|não posso dizer|"
    r"pergunt\w*|procur\w*|fale com|fala com|não falo|não vou (?:falar|dizer|contar)|"
    r"não digo|não conto|não é da sua conta|não te interessa|não interessa)\b", re.I)
_TRAIT_PATTERNS = (
    re.compile(rf"(?P<name>{_CAP})\s*,?\s+(?i:é|era|anda|está)\s+(?P<rest>(?:{_LOW}\s*){{1,4}})"),
    re.compile(rf"(?P<name>{_CAP})\s*[?:,!.…]\s*(?i:um\s+|uma\s+)?(?i:cara|homem|mulher|sujeito|"
               rf"tipo|pessoa)\s+(?P<rest>(?:{_LOW}\s*){{1,3}})"),
)
# A trait in a clause that leaves the subject out ("Lehtinan? Dono. Não fala muito, mas é bom com
# os clientes"): the subject is the last known name of that sentence or the two before it.
_CARRIED_VERBS = ('fala', 'falava', 'gosta', 'gostava', 'bebe', 'bebia', 'trata', 'tratava',
                  'costuma', 'costumava', 'anda', 'andava', 'vive', 'vivia', 'mora', 'morava',
                  'cobra', 'cobrava', 'grita', 'gritava', 'odeia', 'adora', 'ama', 'sorri',
                  'reclama', 'briga', 'confia', 'desconfia', 'trapaceia', 'rouba', 'mente')
TRAIT_ADJECTIVES = frozenset({
    'bom', 'boa', 'bons', 'boas', 'mau', 'má', 'maus', 'más', 'ruim', 'ruins', 'duro', 'dura',
    'gentil', 'simpático', 'simpática', 'antipático', 'antipática', 'generoso', 'generosa',
    'avarento', 'avarenta', 'sovina', 'mesquinho', 'mesquinha', 'honesto', 'honesta',
    'desonesto', 'desonesta', 'justo', 'justa', 'injusto', 'injusta', 'cruel', 'calado',
    'calada', 'quieto', 'quieta', 'falante', 'bravo', 'brava', 'nervoso', 'nervosa', 'tranquilo',
    'tranquila', 'esperto', 'esperta', 'burro', 'burra', 'preguiçoso', 'preguiçosa',
    'trabalhador', 'trabalhadora', 'educado', 'educada', 'grosso', 'grossa', 'rude', 'honrado',
    'honrada', 'perigoso', 'perigosa', 'rico', 'rica', 'pobre', 'bêbado', 'bêbada', 'sério',
    'séria', 'amável', 'legal', 'chato', 'chata', 'severo', 'severa', 'esquisito', 'esquisita'})
_CARRIED = re.compile(
    r"(?:^|(?<=[.!?…])\s*|,\s*(?:mas|e)\s+|\bmas\s+)(?P<clause>(?:não\s+)?(?:ele\s+|ela\s+)?"
    r"(?P<verb>" + '|'.join(_CARRIED_VERBS) + r"|é|era)\b(?P<rest>[^.!?…,]*))", re.I)
_PREPOSITION = re.compile(r"\b(?:em|de|da|do|das|dos|na|no|nas|nos|para|pra|por|pela|pelo|ao|à|"
                          r"até|desde|sobre)\s+$", re.I)
_NUMBER = re.compile(
    r"\b(?:há|faz)\s+(?:mais de\s+|uns\s+|umas\s+|cerca de\s+|quase\s+)?"
    r"(?P<n>\d+|uma|um|duas|dois|três|quatro|cinco|seis|sete|oito|nove|dez|vinte|trinta|"
    r"quarenta|cinquenta|cem|séculos|décadas|anos|meses)\b\s*(?P<unit>anos|décadas|séculos|"
    r"meses|ano|década|século|mês)?", re.I)
_FIRST_PERSON = re.compile(r"\b(?:moro|vivo|estou|trabalho|sou|cheguei|vim)\b", re.I)
_GENERAL = (
    re.compile(r"\b(?:governa|governam|manda|mandam|comanda|comandam)\s+quem\s+(?P<rest>[^.!?…]+)",
               re.I),
    re.compile(r"\bquem\s+(?:tem|tiver|possui)\s+(?P<rest>[\wà-ÿ]+)\s+(?:manda|governa|comanda)",
               re.I),
)
_OPINION = re.compile(r"\b(?:acho|achamos|pra mim|para mim|na minha opinião|não confio|"
                      r"não gosto|parece|parecem|dizem que)\b", re.I)
_SENTENCE = re.compile(r"[^.!?…]+[.!?…]*")


def _forms(word: str) -> tuple[str, ...]:
    return SYNONYMS.get(word.lower(), (word.lower(),))


def _backed(word: str, base: str) -> bool:
    """`word` (or a synonym) appears in `base`, allowing plural/gender endings."""
    for form in _forms(word):
        stem = form[:max(4, len(form) - 3)] if len(form) > 5 else form   # governado ~ governa
        if re.search(r'\b' + re.escape(stem), base):
            return True
    return False


class _Speech:
    def __init__(self, speech: str, context: DialogueContext,
                 asked: Iterable[str] = ()) -> None:
        self.speech = speech
        self.sentences = [(m.start(), m.end()) for m in _SENTENCE.finditer(speech)]
        own = {w.lower() for w in context.persona.display_name.split()}
        asked = {w.lower() for w in asked} - own
        self.known = ({w.lower() for w in context.vocabulary} | asked) - own
        items = context.facts + context.knowledge + context.restricted_knowledge
        self.texts = [f.text.lower() for f in items]
        self.facts = ' '.join(f.text.lower() for f in context.facts)
        # Names the player wrote that are in nothing the speaker knows (not even the vocabulary).
        vocabulary = {w.lower() for w in context.vocabulary}
        self.strangers = {n for n in asked - vocabulary if not self.base([n])}

    def sentence(self, pos: int) -> str:
        return next((self.speech[a:b] for a, b in self.sentences if a <= pos < b), self.speech)

    def opinion(self, pos: int) -> bool:
        return bool(_OPINION.search(self.sentence(pos)))

    def is_known(self, name: str) -> bool:
        return name.lower() in self.known

    def base(self, names: Iterable[str]) -> str:
        names = [n.lower() for n in names]
        return ' '.join(t for t in self.texts if any(n in t for n in names))

    def names_in(self, text: str) -> list[str]:
        return [w for w in re.findall(_CAP, text) if self.is_known(w)]


def _subject_before(s: _Speech, pos: int) -> str | None:
    """The last known name before `pos` in its sentence or the two before it ("Lehtinan? Dono.")."""
    index = next((i for i, (a, b) in enumerate(s.sentences) if a <= pos < b), None)
    if index is None:
        return None
    start = s.sentences[max(0, index - 2)][0]
    # A name after a preposition is a place or an object ("Moro em Athkatla. É bom aqui."),
    # not the subject being described.
    names = [m.group(1) for m in re.finditer(rf"(?<![\wÀ-ÿ])({_CAP})", s.speech[start:pos])
             if s.is_known(m.group(1)) and not _PREPOSITION.search(s.speech[start:start + m.start()])]
    return names[-1] if names else None


def _carried_trait(s: _Speech, m: re.Match) -> bool:
    verb = m.group('verb').lower()
    rest = m.group('rest')
    words = [w for w in re.findall(r'[\wà-ÿ-]+', rest.lower()) if w not in _FILLER]
    if verb in ('é', 'era'):
        if not words or words[0] not in TRAIT_ADJECTIVES:
            return False                      # "É Lehtinan.", "É o que sei."
        claim = words[0]
    else:
        if re.match(r"\s*com\s+(?:ele|ela|[A-ZÀ-Ý])", rest):
            return False                      # "Fala com ele." is advice, not a trait
        claim = verb
    name = _subject_before(s, m.start('clause'))
    if name is None or s.opinion(m.start('clause')):
        return False
    return not _backed(claim, s.base([name]))


def third_party_claim(speech: str, context: DialogueContext,
                      asked: Iterable[str] = ()) -> str | None:
    """The first unbacked claim about someone else ('ROLE', 'STRANGER', 'TRAIT', 'NUMBER',
    'GENERAL').

    `asked` are the names the player wrote: the speaker may repeat them, but a claim about one of
    them still needs backing in what the speaker knows (CR-2026-008)."""
    s = _Speech(speech, context, asked)
    for pattern in _STRANGER_ROLE:
        for m in pattern.finditer(speech):
            if m.group('name').lower() in s.strangers and \
                    m.group('role').lower() not in _NOT_A_ROLE and not s.opinion(m.start('role')):
                return 'ROLE'
    named = [n for n in s.strangers if re.search(rf"(?<![\wÀ-ÿ]){re.escape(n)}(?![\wÀ-ÿ])",
                                                 speech, re.I)]
    if named and not (_IGNORANCE.search(speech) or _OPINION.search(speech)):
        return 'STRANGER'
    for pattern in _ROLE_PATTERNS:
        for m in pattern.finditer(speech):
            role, name = m.group('role').lower(), m.group('name')
            if role in ROLE_WORDS and s.is_known(name) and not s.opinion(m.start('role')) \
                    and not _backed(role, s.base([name])):
                return 'ROLE'
    for pattern in _TRAIT_PATTERNS:
        for m in pattern.finditer(speech):
            name = m.group('name')
            words = [w for w in m.group('rest').lower().split() if w not in _FILLER]
            trait = words[0] if words else None
            if trait is None or trait in ROLE_WORDS or not s.is_known(name) \
                    or s.opinion(m.start('rest')):
                continue
            if not _backed(trait, s.base([name])):
                return 'TRAIT'
    for m in _CARRIED.finditer(speech):
        if _carried_trait(s, m):
            return 'TRAIT'
    for m in _NUMBER.finditer(speech):
        n, unit = m.group('n').lower(), (m.group('unit') or '').lower()
        sentence = s.sentence(m.start())
        # CR-2026-006: a number or a duration is not made true by "acho" ("há séculos, eu acho").
        names = s.names_in(sentence)
        if names:
            base = s.base(names)
        elif _FIRST_PERSON.search(sentence):
            base = s.facts
        else:
            names = s.names_in(speech)          # "Eles governam há décadas": the speech's subject
            if not names:
                continue
            base = s.base(names)
        if n.isdigit() or n in _NUMBER_WORDS:
            digits = n if n.isdigit() else _NUMBER_WORDS[n]
            if not (re.search(r'\b' + digits + r'\b', base) or re.search(r'\b' + n + r'\b', base)):
                return 'NUMBER'
        else:                                    # "há décadas", "há séculos"
            if not any(u in base for u in _UNITS if n.startswith(u) or unit.startswith(u)):
                return 'NUMBER'
    everything = ' '.join(s.texts)
    for pattern in _GENERAL:
        for m in pattern.finditer(speech):
            if s.opinion(m.start()):
                continue
            words = [w for w in re.findall(r'[\wà-ÿ]{4,}', m.group('rest').lower())
                     if w not in _FILLER]
            if words and not any(_backed(w, everything) for w in words):
                return 'GENERAL'
    return None
