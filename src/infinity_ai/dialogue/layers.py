# SPDX-License-Identifier: Apache-2.0
"""ADR-0147: which layer answers a line (code, the local model or Claude) and the code answers.

Simple questions (name, greeting, farewell, what you do, where we are) are answered by code from
what is curated, for everyone. An open question goes by Intelligence and Wisdom and by the
encounter reaction (D1, D6): both scores up to 7 stay with code; a friendly reaction, or either
score from 15, goes to Claude; a negative reaction never does. Nothing here calls a model.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass

from ..personality.identity import em, role_from_name
from .disclosure import CONFIANTE, DESCONFIADO, INTIMO
from .llm import LlmProvider

CODE, LOCAL, CLAUDE = 'CODE', 'LOCAL', 'CLAUDE'
LOW_MAX, HIGH_MIN = 7, 15                     # D1
DEFAULT_SCORE = 10                            # not read: the middle
NEGATIVE = frozenset({'CAUTIOUS', 'THREATENING', 'HOSTILE', 'FLIGHT'})
CLOSED = frozenset({'THREATENING', 'HOSTILE', 'FLIGHT'})
FRIENDLY = 'FRIENDLY'


@dataclass(frozen=True)
class LayerPolicy:
    """The host's choice: layers on, and Claude only when it gave one (ADR-0147, DEC-006)."""
    claude: LlmProvider | None = None


def _score(value: int | None) -> int:
    return value if isinstance(value, int) and 1 <= value <= 25 else DEFAULT_SCORE


def mood(disposition: str | None, trust: str | None = None, companion: bool = False) -> str | None:
    """The reaction that picks the layer; a companion never rolls one, its trust stands in (D6)."""
    if companion:
        if trust in (CONFIANTE, INTIMO):
            return FRIENDLY
        return 'CAUTIOUS' if trust == DESCONFIADO else None
    return disposition


def choose_layer(wisdom: int | None, intelligence: int | None, *,
                 disposition: str | None = None) -> str:
    """D1 and D6, for an open question; `disposition` is already `mood()`."""
    w, i = _score(wisdom), _score(intelligence)
    if w <= LOW_MAX and i <= LOW_MAX:
        return CODE                   # a friendly reaction does not make a simple mind eloquent
    if disposition in NEGATIVE:
        return LOCAL                  # short and curt, never Claude
    if disposition == FRIENDLY or w >= HIGH_MIN or i >= HIGH_MIN:
        return CLAUDE
    return LOCAL


def may_refine(disposition: str | None) -> bool:
    """D3: a line the local model could not get right goes up to Claude, never a negative one."""
    return disposition not in NEGATIVE


# --- simple questions, answered by code -------------------------------------------------------

NAME, GREETING, FAREWELL, OCCUPATION, PLACE = 'NAME', 'GREETING', 'FAREWELL', 'OCCUPATION', 'PLACE'
_INTENTS = (
    (NAME, re.compile(r'(?:e )?(?:qual (?:e )?(?:o )?(?:seu|teu) nome|como (?:voce|tu) se chama|'
                      r'como te chamas?|como (?:e que )?(?:voce )?se chama|quem (?:e|es) (?:voce|tu))')),
    (GREETING, re.compile(r'(?:ola|oi|bom dia|boa tarde|boa noite|saudacoes|salve)'
                          r'(?: (?:amigo|amiga|senhor|senhora|moco|moca))?')),
    (FAREWELL, re.compile(r'(?:tchau|adeus|ate mais|ate logo|ate a proxima|ate breve|'
                          r'fique com os deuses|va com os deuses)(?: (?:amigo|amiga))?')),
    (OCCUPATION, re.compile(r'(?:e )?(?:o que (?:voce|tu) faz(?: aqui| da vida)?|'
                            r'qual (?:e )?(?:o )?(?:seu|teu) (?:trabalho|oficio|servico|profissao)|'
                            r'(?:voce|tu) trabalha com o que|com o que (?:voce|tu) trabalha)')),
    (PLACE, re.compile(r'(?:onde (?:nos )?estamos|que lugar e (?:esse|este)|onde (?:e|fica) aqui|'
                       r'que lugar e aqui)')),
)


def _plain(text: str) -> str:
    text = unicodedata.normalize('NFKD', text.lower())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return ' '.join(re.sub(r'[^a-z0-9 ]+', ' ', text).split())


def simple_intent(text: str) -> str | None:
    """The kind of a whole question that is only a simple one; None for anything more."""
    plain = _plain(text)
    for kind, pattern in _INTENTS:
        if pattern.fullmatch(plain):
            return kind
    return None


def _pick(options: tuple[str, ...], key: str) -> str:
    return options[int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % len(options)]


def _tone(disposition: str | None) -> str:
    return 'closed' if disposition in CLOSED else \
        'cautious' if disposition == 'CAUTIOUS' else 'open'


def has_own_name(name: str) -> bool:
    """A person's name, not what the game calls a generic one ("Plebeu", "Guarda da Cidade")."""
    return bool(name.strip()) and role_from_name(name) is None


def simple_line(kind: str, *, name: str, occupation: str | None, place: str | None,
                disposition: str | None, level: int, key: str) -> str | None:
    """The code answer to a simple question, or None when there is nothing curated to say."""
    tone = _tone(disposition)
    short = level <= 2
    if kind == NAME:
        if not has_own_name(name):
            return None
        if tone == 'closed':
            return _pick(('Não é da sua conta.', 'Que te importa?', 'Não interessa.'), key)
        if tone == 'cautious':
            return _pick((f'{name}. Por quê?', f'Me chamam de {name}. E você, quem é?'), key)
        if short:
            return _pick((f'{name}.', f'Me chamo {name}.'), key)
        line = _pick((f'Me chamo {name}.', f'Meu nome é {name}.'), key)
        return f'{line} Sou {occupation}.' if occupation else line
    if kind == GREETING:
        if tone == 'closed':
            return _pick(('Me deixe em paz.', 'Some daqui.', 'O que foi agora?'), key)
        if tone == 'cautious':
            return _pick(('Hum. O que você quer?', 'Sim? Diga logo.'), key)
        if disposition == FRIENDLY:
            return _pick(('Olá! Precisa de alguma coisa?', 'Olá! Em que posso ajudar?'), key)
        return _pick(('Olá.', 'Oi.') if short else ('Olá. O que deseja?', 'Olá. Pois não?'), key)
    if kind == FAREWELL:
        if tone == 'closed':
            return _pick(('Já vai tarde.', 'Até nunca.'), key)
        if tone == 'cautious':
            return _pick(('Hum.', 'Até.'), key)
        return _pick(('Até mais.', 'Vá com os deuses.', 'Até logo.'), key)
    if kind == OCCUPATION:
        if not occupation:
            return None
        if tone == 'closed':
            return _pick(('Não te interessa.', 'Não é da sua conta.'), key)
        if tone == 'cautious':
            return f'Sou {occupation}. Por que quer saber?'
        return f'Sou {occupation}.'
    if kind == PLACE:
        if not place:
            return None
        if tone == 'closed':
            return _pick(('Descubra sozinho.', 'Não te interessa.'), key)
        return f'Estamos {em(place)}.'
    return None


# --- the code layer, for an open question ------------------------------------------------------

_NAMEWORD = re.compile(r"[A-ZÀ-Ý][\wÀ-ÿ'-]{3,}")
_DONT_KNOW = {
    'open': ('Não entendo disso.', 'Sei não. Isso é coisa de gente estudada.',
             'Hã? Não sei dessas coisas.'),
    'cautious': ('Não sei. Me deixa.', 'Sei de nada, não.'),
    'closed': ('Some daqui.', 'Me deixe em paz.'),
}


def code_line(question: str, known_texts: tuple[str, ...], *, disposition: str | None,
              key: str) -> tuple[str, bool]:
    """(line, unknown) for a simple mind: the popular core of what the question names, else that
    it does not understand. Only the first sentence of a known text is ever said."""
    tone = _tone(disposition)
    if tone != 'closed':
        asked = {w for w in _NAMEWORD.findall(question)}
        for text in known_texts:
            if asked & set(_NAMEWORD.findall(text)):
                first = re.split(r'(?<=[.!?])\s+', text.strip())[0]
                return f'Hum... {first}', False
    return _pick(_DONT_KNOW[tone], key), True


__all__ = ['CODE', 'LOCAL', 'CLAUDE', 'LayerPolicy', 'mood', 'choose_layer', 'may_refine',
           'simple_intent', 'simple_line', 'has_own_name', 'code_line', 'NAME', 'GREETING',
           'FAREWELL', 'OCCUPATION', 'PLACE']
