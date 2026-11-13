# SPDX-License-Identifier: Apache-2.0
"""ADR-0125 (first slice of ADR-0122): encounter reaction, decided by code, expressed by speech.

AD&D 2e DMG Table 59: 2d10, minus the initiator's Charisma reaction adjustment (PHB Table 6; a
positive adjustment improves the reaction, so it is subtracted), crossed with the player
characters' observed conduct (friendly, indifferent, threatening, hostile) gives the NPC's
disposition: flight, friendly, indifferent, cautious, threatening or hostile. Low totals favour
friendlier reactions.

The roll is deterministic (world seed, campaign, branch, person, session), happens once per
person per game session and is recorded as an idempotent event without any text. Companions
never roll. Nothing is written to the game: the disposition only shapes speech and what the
person is willing to tell (`dialogue.context`).
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import unicodedata
from dataclasses import dataclass

from ..state.store import CampaignStore

RULE = 'DMG2e-T59+PHB2e-T6'
POLICY = 'adr-0125-reaction-v1'
REACTION_EVENT = 'NpcEncounterReactionResolved'

FRIENDLY, INDIFFERENT, THREATENING, HOSTILE = 'FRIENDLY', 'INDIFFERENT', 'THREATENING', 'HOSTILE'
CAUTIOUS, FLIGHT = 'CAUTIOUS', 'FLIGHT'
CONDUCTS = (FRIENDLY, INDIFFERENT, THREATENING, HOSTILE)
DISPOSITIONS = (FLIGHT, FRIENDLY, INDIFFERENT, CAUTIOUS, THREATENING, HOSTILE)

_F, _I, _C, _T, _H, _L = FRIENDLY, INDIFFERENT, CAUTIOUS, THREATENING, HOSTILE, FLIGHT
# DMG Table 59 — modified 2d10 total (2 or less .. 20) x PCs' conduct
# (friendly, indifferent, threatening, hostile).
TABLE_59 = {
    2: (_F, _F, _F, _L), 3: (_F, _F, _F, _L), 4: (_F, _F, _C, _L), 5: (_F, _F, _C, _L),
    6: (_F, _F, _C, _C), 7: (_F, _I, _C, _C), 8: (_I, _I, _C, _C), 9: (_I, _I, _C, _T),
    10: (_I, _I, _T, _T), 11: (_I, _I, _T, _T), 12: (_C, _C, _T, _T), 13: (_C, _C, _T, _H),
    14: (_C, _C, _T, _H), 15: (_C, _T, _T, _H), 16: (_T, _T, _H, _H), 17: (_T, _T, _H, _H),
    18: (_T, _T, _H, _H), 19: (_H, _H, _H, _H), 20: (_H, _H, _H, _H),
}
# PHB Table 6 — Charisma score -> reaction adjustment.
PHB_CHARISMA_REACTION = {1: -7, 2: -6, 3: -5, 4: -4, 5: -3, 6: -2, 7: -1, 8: 0, 9: 0, 10: 0,
                         11: 0, 12: 0, 13: 1, 14: 2, 15: 3, 16: 5, 17: 6, 18: 7, 19: 8, 20: 9,
                         21: 10, 22: 11, 23: 12, 24: 13, 25: 14}

# Player conduct from the opening words (local rules, written by us; first match wins).
_HOSTILE = re.compile(r'\b(?:vou te matar|vou matar|morra|morre|maldit[oa]|idiota|imbecil|'
                      r'canalha|verme|desgraçad[oa]|lixo|cale a boca|cala a boca|seu porco|'
                      r'te arrebent|te esfaque|te mato)\b')
_THREAT = re.compile(r'\b(?:senão|se não\b.*\b(?:vai|vou)|é melhor você|ou então|ou vai se|'
                     r'ou eu|te aviso|estou avisando|vai se arrepender|não me faça|me diga agora|'
                     r'fale logo|desembucha)')
_FRIENDLY = re.compile(r'\b(?:olá|ola|oi|bom dia|boa tarde|boa noite|saudações|por favor|'
                       r'obrigad[oa]|com licença|amig[oa]|prazer|perdão|desculpe|gentil)\b')


def classify_conduct(text: str) -> str:
    """FRIENDLY, INDIFFERENT, THREATENING or HOSTILE; indifferent when nothing marks it."""
    low = unicodedata.normalize('NFC', (text or '').lower())
    if _HOSTILE.search(low):
        return HOSTILE
    if _THREAT.search(low):
        return THREATENING
    if _FRIENDLY.search(low):
        return FRIENDLY
    return INDIFFERENT


def charisma_adjustment(score: int | None) -> int:
    return PHB_CHARISMA_REACTION.get(score, 0) if isinstance(score, int) else 0


@dataclass(frozen=True)
class ReactionResult:
    disposition: str
    conduct: str
    dice: tuple[int, int]
    charisma: int | None
    charisma_of: str
    adjustment: int
    total: int
    session: int
    reused: bool = False

    def summary(self) -> str:
        who = f' {self.charisma_of}' if self.charisma_of else ''
        return (f'{self.disposition}(2d10={self.dice[0]}+{self.dice[1]} chr={self.adjustment:+d}'
                f'{who} -> {self.total}, coluna={self.conduct})')


def lookup(total: int, conduct: str) -> str:
    row = TABLE_59[min(20, max(2, total))]
    return row[CONDUCTS.index(conduct)]


def resolve_reaction(conduct: str, charisma: int | None, rng: random.Random, *,
                     charisma_of: str = '', session: int = 0) -> ReactionResult:
    if conduct not in CONDUCTS:
        raise ValueError(f'unknown conduct {conduct}')
    dice = (rng.randint(1, 10), rng.randint(1, 10))
    adjustment = charisma_adjustment(charisma)
    total = dice[0] + dice[1] - adjustment          # a positive adjustment improves the reaction
    return ReactionResult(lookup(total, conduct), conduct, dice, charisma, charisma_of,
                          adjustment, total, session)


def reaction_rng(*, world_seed: str, campaign_id: str, branch_id: str, key: str,
                 session: int) -> random.Random:
    seed = json.dumps([POLICY, world_seed, campaign_id, branch_id, key, session],
                      ensure_ascii=False)
    return random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest(), 'big'))


def reaction_for(store: CampaignStore, branch_id: str, *, key: str, session: int,
                 opening_text: str, charisma: int | None, charisma_of: str, world_seed: str,
                 game_time: int | None, evidence: str = 'LAB_OBSERVED') -> ReactionResult | None:
    """The person's reaction in this session: the recorded one, or resolve and record it now."""
    if not key:
        return None
    for event in reversed(store.visible_events(branch_id, REACTION_EVENT)):
        p = event.payload
        if p.get('npc_key') == key and p.get('session') == session:
            return ReactionResult(p['disposition'], p['conduct'], tuple(p['dice']),
                                  p.get('charisma'), p.get('charisma_of') or '',
                                  p.get('adjustment', 0), p['total'], session, reused=True)
    conduct = classify_conduct(opening_text)
    rng = reaction_rng(world_seed=world_seed, campaign_id=store.campaign_id,
                       branch_id=branch_id, key=key, session=session)
    result = resolve_reaction(conduct, charisma, rng, charisma_of=charisma_of, session=session)
    payload = {'npc_key': key, 'session': session, 'conduct': result.conduct,
               'dice': list(result.dice), 'charisma': result.charisma,
               'charisma_of': result.charisma_of, 'adjustment': result.adjustment,
               'total': result.total, 'disposition': result.disposition, 'rule': RULE,
               'policy': POLICY}
    with store.transaction():
        store.append_event(branch_id=branch_id, host_epoch=session, event_type=REACTION_EVENT,
                           category='CAMPAIGN_OBSERVATION', game_time=game_time,
                           payload=payload, evidence=evidence,
                           idempotency_key=f'reaction|{branch_id}|{key}|{session}')
    return result
