# SPDX-License-Identifier: Apache-2.0
"""ADR-0131 item 2 / SPEC-009: typed absence, answered by code without the model.

When the question is only about what the person cannot answer, the reply is a fixed line of ours:
  NOT_KNOWN   it names something of the pack the person does not hold;
  WITHHELD    it names something the person holds but the per-item decision kept back. The line is
              neutral (maintainer, 2026-11-15): it neither confirms, denies nor lies;
  NOT_DEFINED it asks about the person's own life (family, age, birth, wealth) and no fact says it;
              the person does not invent it nor claims not to know its own life.
Anything else (small talk, a name the pack does not have, something a told item answers) goes to
the model as before. Matching is by names only (the title words, like `mentioned_in`); the titles
of withheld items are used here and never reach the prompt.
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping

from ..memory.common_knowledge import asked_names, says_whole_name, spoken_words, title_words

NOT_KNOWN, NOT_DEFINED, WITHHELD = 'NOT_KNOWN', 'NOT_DEFINED', 'WITHHELD'
KINDS = (NOT_KNOWN, NOT_DEFINED, WITHHELD)
CLOSED = frozenset({'THREATENING', 'HOSTILE', 'FLIGHT'})

# Questions about where the person lives, works or comes from are about itself (the model and the
# self-claim checks answer them), even when they name a place it does not hold.
_ABOUT_SELF = re.compile(r'\b(mora|more|moras|vive|vives|trabalha|trabalhas|nasceu|veio|vem de|'
                         r'é de|és de)\b', re.I)
_YOU = re.compile(r'\b(você|voce|vc|seu|sua|seus|suas|tu|teu|tua|teus|tuas)\b', re.I)
# A closed list of questions about one's own life; each maps to the stem a fact must contain.
_LIFE = {
    r'\bfam[ií]lia\b': 'famíl', r'\bpais?\b': 'pai', r'\bm[ãa]e\b': 'mãe',
    r'\besposa\b': 'espos', r'\bmarido\b': 'marid', r'\bcasad[oa]s?\b': 'casad',
    r'\bfilh[oa]s?\b': 'filh', r'\birm[ãa][osã]?s?\b': 'irm',
    r'\bidade\b': 'idade', r'\bquantos anos\b': 'anos', r'\bnasceu\b|\bnascid[oa]\b': 'nasc',
    r'\bpassado\b': 'passad', r'\bric[oa]s?\b': 'ric', r'\bdinheiro\b': 'dinheir',
}
_LIFE_RE = {re.compile(k, re.I): v for k, v in _LIFE.items()}

LINES = {
    'open': {
        NOT_KNOWN: ('Não sei te dizer.', 'Não faço ideia.', 'Hum, não sei nada sobre isso.',
                    'Isso eu não sei.'),
        NOT_DEFINED: ('Prefiro não falar da minha vida.', 'Isso fica comigo.',
                      'Minha vida não vem ao caso.', 'Não gosto de falar de mim.'),
        WITHHELD: ('Não tenho nada a dizer sobre isso.', 'Disso eu não falo.',
                   'Sobre isso, não tenho o que dizer.', 'Não vou falar disso.'),
    },
    'cautious': {
        NOT_KNOWN: ('Não sei.', 'Não sei nada sobre isso.', 'Não faço ideia.'),
        NOT_DEFINED: ('Isso não vem ao caso.', 'Minha vida é assunto meu.', 'Prefiro não dizer.'),
        WITHHELD: ('Não tenho nada a dizer sobre isso.', 'Sobre isso, nada a dizer.',
                   'Disso eu não falo.'),
    },
    'closed': ('Não tenho nada pra te dizer.', 'Não vou responder.', 'Me deixe em paz.'),
}


def classify_absence(question: str, *, told_texts: Iterable[str],
                     withheld_titles: Iterable[str], unheld_titles: Iterable[str],
                     self_texts: Iterable[str], where_texts: Iterable[str] = (),
                     told_titles: Iterable[str] = (), common: frozenset[str] = frozenset(),
                     aliases: Mapping[str, str] | None = None) -> str | None:
    """The absence kind of this question, or None when the model should answer.

    `told_texts`: every fact and item the person may say (F and released K); `withheld_titles`:
    titles of items it holds but keeps back; `unheld_titles`: titles of pack entries it does not
    hold; `self_texts`: the facts about itself (F); `where_texts`: where it is and its name, which
    keep a question about them from being NOT_KNOWN (but do not answer a withheld item);
    `told_titles`: titles of the items it may say. CR-2026-026: NOT_KNOWN only when no name of
    any unheld entry asked is said in what it tells (Silverymoon is "Lua Prateada" in Alustriel's
    text) and the question names nothing it may tell ("Luskan and Khelben?" is answered).
    CR-2026-027: `common` are ordinary words of titles ("vale", "mar"): alone they do not name an
    entry here, so "Quanto vale?" is not "I don't know"; a whole name or a word of its own does."""
    if not question or not question.strip():
        return None
    asked = spoken_words(question, aliases)
    told: frozenset[str] = frozenset()
    for text in told_texts:
        told |= spoken_words(text)

    def named(titles: Iterable[str]) -> frozenset[str]:
        hits: set[str] = set()
        for title in titles:
            words = title_words(title) & asked
            hits |= words
        return frozenset(hits)

    withheld = named(withheld_titles)
    if withheld and not withheld & told:
        return WITHHELD
    def unheld_named(title: str) -> frozenset[str]:
        names = asked_names(title, asked)
        if says_whole_name(title, asked, common):
            return names                      # a whole name of the entry
        return (title_words(title) & asked) - common   # a word of its own, never a common one

    unheld = [names for names in map(unheld_named, unheld_titles) if names]
    for text in where_texts:
        told |= spoken_words(text)
    if (unheld and not any(words & told for words in unheld) and not named(told_titles)
            and not _ABOUT_SELF.search(question)):
        return NOT_KNOWN
    if _YOU.search(question):
        own = ' '.join(self_texts).lower()
        for pattern, stem in _LIFE_RE.items():
            if pattern.search(question) and stem not in own:
                return NOT_DEFINED
    return None


def absence_line(kind: str, disposition: str | None, key: str) -> str:
    """A fixed line for this kind and encounter tone, chosen stably by `key` (person + question)."""
    if kind not in KINDS:
        raise ValueError(f'unknown absence kind {kind!r}')
    if disposition in CLOSED:
        options = LINES['closed']
    else:
        options = LINES['cautious' if disposition == 'CAUTIOUS' else 'open'][kind]
    index = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % len(options)
    return options[index]
