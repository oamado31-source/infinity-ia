# SPDX-License-Identifier: Apache-2.0
"""ADR-0126 (second slice of ADR-0122): morale check in dialogue, decided by code.

AD&D 2e DMG, chapter 9: when a situation calls for it, roll 2d10; a total at or below the
modified morale keeps the creature's resolve (HOLD), a higher total means it gives in (YIELD).
In dialogue the triggers are a bribe (temptation), intimidation (facing an obviously superior
force) and a request to act against someone the person is tied to (conflict with an employer).

Base morale comes from DMG Table 49 by role (regular soldiers 12 for guards and fighters, the
average 0-level human 7 for everyone else) unless a checked curation sets it. Modifiers, from
Table 50: lawful +1, chaotic -1 (never twice), the player's treatment in that very line —
courteous +2 ("favored"), threatening or hostile -4 ("poorly treated").

One check per trigger per person per game session, rolled deterministically and recorded as an
idempotent event without text. Speech only: a bribe moves no gold in the game.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from collections.abc import Iterable
from dataclasses import dataclass

from ..state.store import CampaignStore
from .reaction import FRIENDLY, HOSTILE, THREATENING, classify_conduct
from .style import GAME_ALIGNMENT

RULE = 'DMG2e-ch9-T49-T50'
POLICY = 'adr-0126-morale-v1'
MORALE_EVENT = 'NpcMoraleCheckResolved'
BRIBE, INTIMIDATION, BETRAYAL = 'BRIBE', 'INTIMIDATION', 'BETRAYAL'
TRIGGERS = (BRIBE, INTIMIDATION, BETRAYAL)
HOLD, YIELD = 'HOLD', 'YIELD'

# DMG Table 49 by role (ADR-0117 roles); everyone not listed is an average 0-level human.
TABLE_49_BY_ROLE = {'GUARD': 12, 'FIGHTER': 12}
AVERAGE_HUMAN = 7

_BETRAY_VERB = re.compile(r'\b(?:contra|trair|traia|traí|roub\w*|engan\w*|escond\w* d[oa]|'
                          r'não cont\w* (?:a|ao|à|pro|pra)|delat\w*|sabot\w*|envenen\w*|'
                          r'passar a perna)\b', re.I)
_INTIMIDATE = re.compile(r'\b(?:te mato|vou te matar|te matar|te machuc\w*|vou te ferir|'
                         r'te arrebent\w*|te esfaque\w*|te quebr\w*|cortar sua|corto sua|'
                         r'(?:fale|diga|conte|responda)\b[^.!?]{0,40}\bou (?:eu )?(?:te|vai)|'
                         r'senão (?:eu )?te\b)', re.I)
_BRIBE = re.compile(r'\b(?:te pago|pago|pagar|pagarei|moedas?|ouro|peças? de ouro|recompens\w*|'
                    r'gorjeta|suborn\w*|dinheiro|te dou|te darei|em troca)\b', re.I)


def classify_trigger(text: str, ties: Iterable[str] = ()) -> str | None:
    """BETRAYAL (a betrayal verb and someone the person is tied to), INTIMIDATION or BRIBE."""
    low = text or ''
    names = [t for t in ties if t]
    if names and _BETRAY_VERB.search(low) and any(
            re.search(r'\b' + re.escape(n) + r'\b', low, re.I) for n in names):
        return BETRAYAL
    if _INTIMIDATE.search(low):
        return INTIMIDATION
    if _BRIBE.search(low):
        return BRIBE
    return None


def base_morale(role: str | None, curated: int | None = None) -> int:
    if isinstance(curated, int) and 2 <= curated <= 20:
        return curated
    return TABLE_49_BY_ROLE.get(role or '', AVERAGE_HUMAN)


def ethical_axis(game_alignment: int | None = None, profile: dict | None = None) -> str | None:
    if profile and isinstance(profile.get('alignment_initial'), dict):
        return profile['alignment_initial'].get('ethical')
    axes = GAME_ALIGNMENT.get(game_alignment) if isinstance(game_alignment, int) else None
    return axes[0] if axes else None


def modifiers(*, ethical: str | None, text: str) -> tuple[tuple[str, int], ...]:
    """Table 50 modifiers that apply; each one at most once."""
    out = []
    if ethical == 'LAWFUL':
        out.append(('lawful', 1))
    elif ethical == 'CHAOTIC':
        out.append(('chaotic', -1))
    conduct = classify_conduct(text)
    if conduct == FRIENDLY:
        out.append(('favored', 2))
    elif conduct in (THREATENING, HOSTILE):
        out.append(('poorly_treated', -4))
    return tuple(out)


@dataclass(frozen=True)
class MoraleResult:
    trigger: str
    outcome: str
    dice: tuple[int, int]
    base: int
    mods: tuple[tuple[str, int], ...]
    morale: int
    total: int
    reused: bool = False

    def summary(self) -> str:
        mod = sum(v for _, v in self.mods)
        return (f'{self.trigger}:{self.outcome}(2d10={self.dice[0]}+{self.dice[1]} vs '
                f'{self.base}{mod:+d}={self.morale})')


def resolve_morale(trigger: str, base: int, mods: tuple[tuple[str, int], ...],
                   rng: random.Random) -> MoraleResult:
    if trigger not in TRIGGERS:
        raise ValueError(f'unknown trigger {trigger}')
    dice = (rng.randint(1, 10), rng.randint(1, 10))
    morale = base + sum(v for _, v in mods)
    total = dice[0] + dice[1]
    return MoraleResult(trigger, HOLD if total <= morale else YIELD, dice, base, mods, morale,
                        total)


def morale_rng(*, world_seed: str, campaign_id: str, branch_id: str, key: str, session: int,
               trigger: str) -> random.Random:
    seed = json.dumps([POLICY, world_seed, campaign_id, branch_id, key, session, trigger],
                      ensure_ascii=False)
    return random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest(), 'big'))


def morale_for(store: CampaignStore, branch_id: str, *, key: str, session: int, trigger: str,
               base: int, mods: tuple[tuple[str, int], ...], world_seed: str,
               game_time: int | None, evidence: str = 'LAB_OBSERVED') -> MoraleResult | None:
    """This trigger's check for the person in this session: recorded, or resolved and recorded."""
    if not key or trigger not in TRIGGERS:
        return None
    for event in reversed(store.visible_events(branch_id, MORALE_EVENT)):
        p = event.payload
        if p.get('npc_key') == key and p.get('session') == session and p.get('trigger') == trigger:
            return MoraleResult(trigger, p['outcome'], tuple(p['dice']), p['base'],
                                tuple((m[0], m[1]) for m in p.get('modifiers') or ()),
                                p['morale'], p['total'], reused=True)
    rng = morale_rng(world_seed=world_seed, campaign_id=store.campaign_id, branch_id=branch_id,
                     key=key, session=session, trigger=trigger)
    result = resolve_morale(trigger, base, mods, rng)
    payload = {'npc_key': key, 'session': session, 'trigger': trigger, 'outcome': result.outcome,
               'dice': list(result.dice), 'base': base, 'modifiers': [list(m) for m in mods],
               'morale': result.morale, 'total': result.total, 'rule': RULE, 'policy': POLICY}
    with store.transaction():
        store.append_event(branch_id=branch_id, host_epoch=session, event_type=MORALE_EVENT,
                           category='CAMPAIGN_OBSERVATION', game_time=game_time,
                           payload=payload, evidence=evidence,
                           idempotency_key=f'morale|{branch_id}|{key}|{session}|{trigger}')
    return result
