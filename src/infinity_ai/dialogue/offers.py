# SPDX-License-Identifier: Apache-2.0
"""ADR-0132: a person who sells goods or services never says it does not offer them.

What it sells comes from the stores its dialogue opens in the game (`gamedata.inventory.Offer`,
built locally, never in the repository). This module turns that into facts about the person,
finds a denial of what it sells in a reply, and writes the line used when the model keeps denying.
Matching is by plain words (no model).
"""
from __future__ import annotations

import re

from ..gamedata.inventory import Offer

COIN = 'peças de ouro'
ROOM_NAMES = {'PEASANT': 'camponês', 'MERCHANT': 'mercador', 'NOBLE': 'nobre', 'ROYAL': 'real'}
CATEGORY_NAMES = {
    'QUARTOS': 'quartos', 'BEBIDAS': 'bebidas', 'ARMAS': 'armas', 'ARMADURAS': 'armaduras',
    'ESCUDOS': 'escudos', 'JOIAS': 'joias', 'POCOES': 'poções', 'PERGAMINHOS': 'pergaminhos',
    'ROUPAS': 'mantos, botas e cintos', 'VARINHAS': 'varinhas', 'CURAS': 'curas',
    'OUTROS': 'outras mercadorias',
}
# Words that name each kind of thing a person sells (singular and plural, lowercase).
CATEGORY_WORDS = {
    'QUARTOS': ('quarto', 'quartos', 'hospedagem', 'estadia', 'pernoite', 'pernoitar', 'dormir',
                'cama', 'camas', 'hospedar', 'alugar', 'aluguel'),
    'BEBIDAS': ('bebida', 'bebidas', 'cerveja', 'cervejas', 'vinho', 'vinhos', 'hidromel',
                'beber', 'caneca', 'cerva', 'birita'),
    'ARMAS': ('arma', 'armas', 'espada', 'espadas', 'adaga', 'adagas', 'machado', 'machados',
              'arco', 'arcos', 'flecha', 'flechas', 'besta', 'bestas', 'lança', 'lanças', 'maça',
              'maças', 'mangual', 'martelo', 'martelos', 'cimitarra', 'katana', 'clava', 'cajado',
              'alabarda', 'funda', 'dardo', 'dardos'),
    'ARMADURAS': ('armadura', 'armaduras', 'elmo', 'elmos', 'cota', 'couraça', 'malha'),
    'ESCUDOS': ('escudo', 'escudos', 'broquel'),
    'JOIAS': ('joia', 'joias', 'jóia', 'jóias', 'anel', 'anéis', 'amuleto', 'amuletos', 'colar',
              'colares', 'gema', 'gemas'),
    'POCOES': ('poção', 'poções', 'pocao', 'pocoes', 'elixir'),
    'PERGAMINHOS': ('pergaminho', 'pergaminhos'),
    'ROUPAS': ('manto', 'mantos', 'capa', 'capas', 'bota', 'botas', 'cinto', 'cintos'),
    'VARINHAS': ('varinha', 'varinhas'),
    'CURAS': ('cura', 'curas', 'curar', 'curativo', 'bênção'),
}
MAX_ITEM_LINES = 8
_WORD = re.compile(r"[\wÀ-ÖØ-öø-ÿ'-]+")
_SENTENCE = re.compile(r'[^.!?…]+[.!?…]*')
# "não vendo", "não temos", "não alugo", "aqui não tem", "não servimos", "não há"...
_DENIAL = re.compile(
    r'\b(?:não|nao|nunca|nem)\s+(?:\w+\s+){0,2}?(?:vend\w*|tem|temos|tenho|têm|há|alug\w*|'
    r'serv\w*|ofere\w*|trabalh\w* com|mexo com|fazemos|faço|cur\w*)\b', re.I)
_IGNORANCE = re.compile(
    r'\b(?:não sei|sei lá|não faço (?:a menor )?ideia|não tenho (?:a menor )?ideia|desconheço|'
    r'não conheço)\b', re.I)


def offered(offer: Offer | None) -> set[str]:
    """The categories this person sells."""
    if offer is None:
        return set()
    cats = {c for _, _, c in offer.items}
    if offer.rooms:
        cats.add('QUARTOS')
    if offer.drinks:
        cats.add('BEBIDAS')
    if offer.cures:
        cats.add('CURAS')
    return cats


def _words(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text or '')}


def _stems(text: str) -> set[str]:
    """Words without a plural -s, so "espadas" finds "Espada Longa" (lab, 2026-11-17)."""
    return {w[:-1] if len(w) > 4 and w.endswith('s') else w for w in _words(text)}


def _priced(offer: Offer, cat: str) -> list[tuple[str, int, str]]:
    """Items of a category that have a price (a free item is ammunition or a store oddity)."""
    return [i for i in offer.items if i[2] == cat and i[1] > 0]


def categories_in(text: str, cats: set[str] | None = None) -> set[str]:
    """Categories (of `cats`, or all) a text names by their words."""
    words = _words(text)
    return {c for c, ws in CATEGORY_WORDS.items()
            if (cats is None or c in cats) and words & set(ws)}


# Lab, 2026-11-17 (mantenedor): a seller does not know an item is "+1"; it knows it is enchanted,
# of high quality and more expensive. Game bonuses never reach the person.
_BONUS = re.compile(r'\s*[+-]\d+\b')


def _special(name: str) -> bool:
    return bool(_BONUS.search(name))


def _price(price: int) -> str:
    return f'{price} peça de ouro' if price == 1 else f'{price} {COIN}'


def _rooms(offer: Offer) -> str:
    return ', '.join(f'{ROOM_NAMES[t]} {p}' for t, p in offer.rooms) + f' {COIN} por noite'


def _drinks(offer: Offer) -> str:
    return ', '.join(f'{n} {p}' for n, p in offer.drinks) + f' {COIN}'


def _place(offer: Offer) -> str:
    named = offer.place and offer.place.lower() not in {'comerciante', 'loja', 'mercador'}
    return f' na {offer.place}' if named else ''


def offer_facts(offer: Offer | None, question: str = '') -> list[str]:
    """Facts about what the person sells: one summary line, plus the items the question names."""
    cats = offered(offer)
    if offer is None or not cats:
        return []
    parts = []
    if offer.rooms:
        parts.append(f'quartos ({_rooms(offer)})')
    if offer.drinks:
        parts.append(f'bebidas ({_drinks(offer)})')
    goods = [CATEGORY_NAMES[c] for c in CATEGORY_NAMES if c in cats
             and c not in ('QUARTOS', 'BEBIDAS', 'CURAS') and _priced(offer, c)]
    if goods:
        parts.append(', '.join(goods))
    if offer.cures:
        parts.append('curas (' + ', '.join(f'{n} {p}' for n, p in offer.cures) + f' {COIN})')
    facts = [f'Você vende{_place(offer)}: ' + '; '.join(parts) + '.']
    asked = _stems(question)
    for cat in sorted(categories_in(question, cats) - {'QUARTOS', 'BEBIDAS', 'CURAS'}):
        items = _priced(offer, cat)
        plain = [i for i in items if not _special(i[0])]
        special = [i for i in items if _special(i[0])]
        special = [i for i in special if _stems(i[0]) & asked] or special   # of the kind asked
        named = [i for i in plain if _stems(i[0]) & asked]
        shown = (named or plain)[:MAX_ITEM_LINES]
        line = ', '.join(f'{n} ({_price(p)})' for n, p, _ in shown)
        if special:
            cheapest = min(p for _, p, _ in special)
            extra = (f'algumas peças especiais, encantadas e de alta qualidade, bem mais caras '
                     f'(a partir de {_price(cheapest)})')
            line = f'{line}; e também {extra}' if line else extra
        if line:
            facts.append(f'Na sua loja, {CATEGORY_NAMES[cat]}: {line}.')
    return facts


def denied_offer(speech: str, question: str | None, offer: Offer | None) -> str | None:
    """The category the reply denies selling (or says it does not know about), or None."""
    cats = offered(offer)
    if not cats or not speech:
        return None
    for match in _SENTENCE.finditer(speech):
        sentence = match.group(0)
        if _DENIAL.search(sentence):
            hit = categories_in(sentence, cats)
            if hit:
                return sorted(hit)[0]
    asked = categories_in(question or '', cats)
    if asked and _IGNORANCE.search(speech) and not re.search(r'\d', speech):
        return sorted(asked)[0]
    return None


def offer_line(offer: Offer | None, question: str = '') -> str | None:
    """A plain seller's answer for when the model keeps denying what it sells."""
    cats = offered(offer)
    if offer is None or not cats:
        return None
    asked = categories_in(question, cats) or cats
    if 'QUARTOS' in asked and offer.rooms:
        return f'Temos quartos, sim: {_rooms(offer)}.'
    if 'BEBIDAS' in asked and offer.drinks:
        named = [d for d in offer.drinks if _stems(d[0]) & _stems(question) - {'cerveja'}]
        shown = (named or list(offer.drinks))[:3]
        return 'Temos, sim: ' + ', '.join(f'{n} por {_price(p)}' for n, p in shown) + '.'
    if 'CURAS' in asked and offer.cures:
        return 'Fazemos curas, sim: ' + ', '.join(f'{n} {p}' for n, p in offer.cures) + f' {COIN}.'
    goods = [c for c in CATEGORY_NAMES if c in asked and c not in ('QUARTOS', 'BEBIDAS', 'CURAS')]
    if goods:
        items = [i for i in _priced(offer, goods[0]) if not _special(i[0])]
        items = ([i for i in items if _stems(i[0]) & _stems(question)] or items)[:3]
        if items:
            return (f'Tenho {CATEGORY_NAMES[goods[0]]}, sim: '
                    + ', '.join(f'{n} por {_price(p)}' for n, p, _ in items) + '. Dê uma olhada.')
    return 'Tenho, sim. Dê uma olhada no que vendo.'
