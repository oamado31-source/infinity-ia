# SPDX-License-Identifier: Apache-2.0
"""SPEC-004 / ADR-0106: local LLM provider (Ollama) and a fake for tests.

The model only drafts the NPC's line as JSON; it never decides facts, ACL or game state, and its
output is validated before anyone sees it. There is no remote provider in this stage.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from typing import Any, Protocol

REPLY_SCHEMA: dict[str, Any] = {
    'type': 'object',
    'properties': {
        'speech': {'type': 'string'},
        'used_facts': {'type': 'array', 'items': {'type': 'string'}},
        'unknown': {'type': 'boolean'},
    },
    'required': ['speech', 'used_facts', 'unknown'],
}


class LlmError(RuntimeError):
    """Model unavailable, timed out or returned something unusable."""


class LlmProvider(Protocol):
    model: str

    def generate(self, messages: Sequence[dict[str, str]]) -> str: ...


class OllamaProvider:
    def __init__(self, model: str = 'qwen3:30b-a3b', *, base_url: str = 'http://127.0.0.1:11434',
                 timeout_s: float = 30.0, temperature: float = 0.6, max_tokens: int = 220,
                 num_ctx: int = 8192) -> None:
        self.model, self._url, self._timeout = model, base_url.rstrip('/') + '/api/chat', timeout_s
        # ADR-0127: without num_ctx Ollama uses the model's own context (262144 for qwen3:30b-a3b,
        # about 45 GB loaded), which starves the local STT of memory. Our prompts fit in 8192.
        self._options = {'temperature': temperature, 'num_predict': max_tokens,
                         'num_ctx': num_ctx}

    def generate(self, messages: Sequence[dict[str, str]]) -> str:
        body = json.dumps({'model': self.model, 'stream': False, 'think': False,
                           'format': REPLY_SCHEMA, 'options': self._options,
                           'messages': list(messages)}).encode('utf-8')
        request = urllib.request.Request(self._url, data=body,
                                         headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                doc = json.loads(response.read().decode('utf-8'))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise LlmError(f'ollama request failed: {exc}') from exc
        content = (doc.get('message') or {}).get('content')
        if not isinstance(content, str) or not content.strip():
            raise LlmError('empty model reply')
        return content


class FakeProvider:
    """Returns scripted replies (str) or raises scripted exceptions, recording the prompts."""

    def __init__(self, replies: Sequence[str | Exception] | Callable[[list], str],
                 model: str = 'fake') -> None:
        self.model = model
        self._replies = replies if callable(replies) else list(replies)
        self.calls: list[list[dict[str, str]]] = []

    def generate(self, messages: Sequence[dict[str, str]]) -> str:
        self.calls.append([dict(m) for m in messages])
        if callable(self._replies):
            return self._replies(self.calls[-1])
        if not self._replies:
            raise LlmError('no scripted reply left')
        reply = self._replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply
