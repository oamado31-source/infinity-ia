# SPDX-License-Identifier: Apache-2.0
"""ADR-0123: the turns of the conversation in progress, kept only in the service's memory.

A conversation is one opening of the in-game box with one person. Its last turns (what the
player asked and what the person answered, fallback included, as the player saw it) go back to
the model so follow-ups make sense ("e quem é então?", "ele trabalha aqui?"). Nothing is written
to disk or to the campaign database; restarting the service forgets everything.
"""
from __future__ import annotations

from collections import OrderedDict, deque

MAX_TURNS = 4            # turns kept per conversation
MAX_CONVERSATIONS = 64   # open conversations remembered at once (oldest dropped first)
MAX_TURN_CHARS = 300     # each side of a turn is cut to this length

Turn = tuple[str, str]   # (player text, speech the player saw)


def _cut(text: str) -> str:
    text = ' '.join(str(text).split())
    return text if len(text) <= MAX_TURN_CHARS else text[:MAX_TURN_CHARS - 1] + '…'


class ConversationMemory:
    """Last turns per (conversation id, npc id); in memory only."""

    def __init__(self, max_turns: int = MAX_TURNS,
                 max_conversations: int = MAX_CONVERSATIONS) -> None:
        self._max_turns = max_turns
        self._max_conversations = max_conversations
        self._turns: OrderedDict[tuple[str, str], deque[Turn]] = OrderedDict()
        self._count: dict[tuple[str, str], int] = {}

    def history(self, conversation_id: str | None, npc_id: str) -> tuple[Turn, ...]:
        if not conversation_id or not npc_id:
            return ()
        return tuple(self._turns.get((conversation_id, npc_id), ()))

    def add(self, conversation_id: str | None, npc_id: str, player: str, speech: str) -> int:
        """Record a turn; returns the turn number in this conversation (0 = not recorded)."""
        if not conversation_id or not npc_id or not player or not speech:
            return 0
        key = (conversation_id, npc_id)
        turns = self._turns.get(key)
        if turns is None:
            turns = self._turns[key] = deque(maxlen=self._max_turns)
            while len(self._turns) > self._max_conversations:
                old, _ = self._turns.popitem(last=False)
                self._count.pop(old, None)
        self._turns.move_to_end(key)
        turns.append((_cut(player), _cut(speech)))
        self._count[key] = self._count.get(key, 0) + 1
        return self._count[key]
