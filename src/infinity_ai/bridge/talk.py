# SPDX-License-Identifier: Apache-2.0
"""In-game dialogue box protocol (INQUIRY channel; `tools/eeex-probe/M_INFAIT.lua`).

Requests arrive as `INFAI-TALK {json}` lines in the loader log. Like every other log line, they are
untrusted (any mod can print). Parsing is therefore strict: script names, area and lengths are
validated, and the player's text is kept only in memory (ADR-0107 item 6). Replies go back as a
tiny Lua file (`override/INFAIRSP.lua`) that the box re-reads with `Infinity_DoFile`. The file
defines only `INFAI_TALK_Reply` with two escaped string literals, so model output can never become
Lua code.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

TALK_PREFIX = 'INFAI-TALK '
TALK_SCHEMA = 'infinity-ai.talk.v1'
REPLY_RESREF = 'INFAIRSP'
MAX_TEXT = 500
MAX_SPEECH = 600
_MAX_LINE = 8192
_MAX_LISTENERS = 5
_RESREF = re.compile(r'[A-Za-z0-9_#-]{1,8}')
_SCRIPT_NAME = re.compile(r'[A-Za-z0-9_#-]{1,32}')
_REQ_ID = re.compile(r'[0-9]{1,10}-[0-9]{1,12}-[0-9]{1,8}')
# Saved games replace the first letter of an area actor's CRE resref with '*'.
_CONV = re.compile(r'\d{1,15}-\d{1,15}')     # ADR-0123: "<session>-<clock_ms>" per box opening
_CRE = re.compile(r'(?=.{1,8}$)\*?[A-Za-z0-9_#-]+')
INPUTS = frozenset({'TEXT', 'VOICE'})


@dataclass(frozen=True)
class TalkRequest:
    req_id: str
    session_seq: int
    clock_ms: int
    area: str | None
    game_time: int | None
    input: str
    speaker_script: str          # '' when the creature has no script name
    speaker_name: str
    speaker_cre: str | None
    speaker_dead: bool
    text: str
    listeners: tuple[str, ...] | None   # companion ids (`npc:<script>`), None = could not read
    speaker_instance: int | None = None  # engine object id: unique in this session and area
    speaker_party: bool = False          # a companion in the party (talks as a companion)
    speaker_wisdom: int | None = None    # ability scores from the creature (ADR-0117 tier);
    speaker_intelligence: int | None = None  # None = not read
    conversation_id: str | None = None   # ADR-0123: one per box opening; None = old box

    @property
    def speaker_id(self) -> str | None:
        """`npc:<script>`; without a script name, `npc:cre-<resref>` (gamedata residents)."""
        if self.speaker_script:
            return f'npc:{self.speaker_script.lower()}'
        if self.speaker_cre and not self.speaker_cre.startswith('*'):
            return f'npc:cre-{self.speaker_cre.lower()}'
        return None          # '*XXXX' needs the area's residents to resolve (in_game)


def _ability(value: object) -> int | None:
    """An AD&D ability score (1..25); anything else (0 = not read) is unknown."""
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 25:
        return None
    return value


def _int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def parse_talk_line(line: str) -> TalkRequest | None:
    """One log line -> request, or None for anything malformed."""
    index = line.find(TALK_PREFIX)
    if index < 0:
        return None
    payload = line[index + len(TALK_PREFIX):].strip()
    if not payload or len(payload) > _MAX_LINE:
        return None
    try:
        doc = json.loads(payload)
    except ValueError:
        return None
    if not isinstance(doc, dict) or doc.get('schema') != TALK_SCHEMA:
        return None
    req_id, speaker, text = doc.get('req_id'), doc.get('speaker'), doc.get('text')
    session_seq, clock_ms = _int(doc.get('session_seq')), _int(doc.get('clock_ms'))
    if not isinstance(req_id, str) or not _REQ_ID.fullmatch(req_id) or session_seq is None \
            or clock_ms is None or not isinstance(speaker, dict):
        return None
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT:
        return None
    if doc.get('input') not in INPUTS:
        return None
    script, name, dead = speaker.get('script'), speaker.get('name'), speaker.get('dead')
    if not isinstance(script, str) or (script and not _SCRIPT_NAME.fullmatch(script)) \
            or not isinstance(name, str) or len(name) > 64 or not isinstance(dead, bool):
        return None
    cre = speaker.get('cre')
    cre = cre.upper() if isinstance(cre, str) and _CRE.fullmatch(cre) else None
    area = doc.get('area')
    area = area if isinstance(area, str) and _RESREF.fullmatch(area) else None
    listeners = doc.get('listeners')
    if listeners is not None:
        if not isinstance(listeners, list) or len(listeners) > _MAX_LISTENERS or not all(
                isinstance(n, str) and _SCRIPT_NAME.fullmatch(n) and n != 'None' for n in listeners):
            return None
        listeners = tuple(sorted({f'npc:{n.lower()}' for n in listeners}))
    return TalkRequest(req_id, session_seq, clock_ms, area, _int(doc.get('game_time')),
                       doc['input'], script, name, cre, dead, text.strip(), listeners,
                       _int(speaker.get('instance')), speaker.get('party') is True,
                       _ability(speaker.get('wis')), _ability(speaker.get('int')),
                       conv if isinstance(conv := doc.get('conv'), str)
                       and _CONV.fullmatch(conv) else None)


def parse_talk_requests(text: str) -> list[TalkRequest]:
    """Every valid request in the log text, oldest first (an unterminated last line is skipped)."""
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith(('\n', '\r')):
        lines.pop()
    out = []
    for line in lines:
        request = parse_talk_line(line)
        if request is not None:
            out.append(request)
    return out


def lua_string(value: str) -> str:
    """A Lua double-quoted literal that cannot break out: \\, quotes and controls become \\ddd."""
    out = []
    for ch in value:
        code = ord(ch)
        if ch in '"\\' or code < 0x20 or code == 0x7F:
            out.append(f'\\{code:03d}')
        else:
            out.append(ch)
    return '"' + ''.join(out) + '"'


PLACEHOLDER_REPLY = 'INFAI_TALK_Reply = {req_id = "", speech = ""}\n'
"""Kept in override/ at all times: the engine only finds override files present at launch."""


def render_reply(req_id: str, speech: str) -> str:
    """Contents of `override/INFAIRSP.lua` for one reply."""
    if not _REQ_ID.fullmatch(req_id):
        raise ValueError('bad req_id')
    speech = ' '.join(speech.split())[:MAX_SPEECH]
    return f'INFAI_TALK_Reply = {{req_id = {lua_string(req_id)}, speech = {lua_string(speech)}}}\n'
