# SPDX-License-Identifier: Apache-2.0
"""SPEC-004 / ADR-0106: local LLM provider (Ollama), the Claude provider (ADR-0147) and a fake.

The model only drafts the NPC's line as JSON; it never decides facts, ACL or game state, and its
output is validated before anyone sees it. The Claude provider is opt-in (ADR-0147, DEC-006): it
is only built when the host asks for it, and its key comes from the host's environment.
"""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from pathlib import Path
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
                 num_ctx: int = 8192, keep_alive: str = '30m') -> None:
        self.model, self._url, self._timeout = model, base_url.rstrip('/') + '/api/chat', timeout_s
        # ADR-0127: without num_ctx Ollama uses the model's own context (262144 for qwen3:30b-a3b,
        # about 45 GB loaded), which starves the local STT of memory. Our prompts fit in 8192.
        self._options = {'temperature': temperature, 'num_predict': max_tokens,
                         'num_ctx': num_ctx}
        # S1i: Ollama unloads a model after 5 idle minutes by default; reloading 19 GB took longer
        # than the dialogue timeout, so the reply fell back. Keep it loaded between talks.
        self._keep_alive = keep_alive

    def generate(self, messages: Sequence[dict[str, str]]) -> str:
        body = json.dumps({'model': self.model, 'stream': False, 'think': False,
                           'format': REPLY_SCHEMA, 'options': self._options,
                           'keep_alive': self._keep_alive,
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


CLAUDE_MODEL = 'claude-haiku-5-5'
# The API's structured output needs every object closed.
CLAUDE_REPLY_SCHEMA: dict[str, Any] = {**REPLY_SCHEMA, 'additionalProperties': False}
# US$ per million tokens (input, output); cache reads cost 0.1x and cache writes 1.25x the input.
CLAUDE_PRICES = {'claude-haiku-5-5': (0.10, 0.50)}
USAGE_FIELDS = ('input_tokens', 'output_tokens', 'cache_read_input_tokens',
                'cache_creation_input_tokens')


def claude_cost(model: str, usage: dict[str, int]) -> float | None:
    """Estimated US$ of the given usage, or None for a model without a known price."""
    price = CLAUDE_PRICES.get(model)
    if price is None:
        return None
    inp, out = price
    return (usage.get('input_tokens', 0) * inp + usage.get('output_tokens', 0) * out
            + usage.get('cache_read_input_tokens', 0) * inp * 0.1
            + usage.get('cache_creation_input_tokens', 0) * inp * 1.25) / 1_000_000


class AnthropicProvider:
    """ADR-0147: the NPC's line drafted by Claude, with the same contract as Ollama.

    The first system message (rules, persona, allowed facts) becomes the API's system prompt,
    marked for the prompt cache; later system messages (retry hints) stay in place, which the
    model accepts mid-conversation. Thinking is off and effort low, so the line comes fast; the
    reply is the same JSON, enforced by the API's structured output and validated as always.
    The key is never passed here: the SDK reads it from the host's environment."""

    def __init__(self, model: str = CLAUDE_MODEL, *, timeout_s: float = 30.0,
                 max_tokens: int = 400, client: Any = None) -> None:
        self.model, self._max_tokens = model, max_tokens
        if client is None:
            import anthropic                      # optional dependency: only when asked for
            client = anthropic.Anthropic(timeout=timeout_s, max_retries=1)
        self._client = client
        self.last_usage: dict[str, int] = {}
        self.usage_total: dict[str, int] = dict.fromkeys(USAGE_FIELDS, 0)
        self.requests = 0

    def generate(self, messages: Sequence[dict[str, str]]) -> str:
        messages = list(messages)
        system = []
        if messages and messages[0]['role'] == 'system':
            system = [{'type': 'text', 'text': messages.pop(0)['content'],
                       'cache_control': {'type': 'ephemeral'}}]
        try:
            response = self._client.messages.create(
                model=self.model, max_tokens=self._max_tokens, system=system,
                messages=[{'role': m['role'], 'content': m['content']} for m in messages],
                thinking={'type': 'disabled'},
                output_config={'effort': 'low',
                               'format': {'type': 'json_schema',
                                          'schema': CLAUDE_REPLY_SCHEMA}})
        except Exception as exc:    # no key, no network, timeout, API error: model unavailable
            raise LlmError(f'claude request failed: {type(exc).__name__}: {exc}') from exc
        self.requests += 1
        usage = getattr(response, 'usage', None)
        self.last_usage = {f: int(getattr(usage, f, 0) or 0) for f in USAGE_FIELDS}
        for f in USAGE_FIELDS:
            self.usage_total[f] += self.last_usage[f]
        if response.stop_reason == 'refusal':
            raise LlmError('claude refused')
        content = ''.join(b.text for b in response.content if getattr(b, 'type', '') == 'text')
        if not content.strip():
            raise LlmError('empty model reply')
        return content


class MonthlyBudget:
    """ADR-0147 D5: the host's monthly spending cap, counted locally from the API's usage.

    The ledger is a small JSON file outside the repository ({"2026-11": 0.0123, ...}); it only
    holds money, never text."""

    def __init__(self, path: Path, cap_usd: float, *,
                 month: Callable[[], str] = lambda: time.strftime('%Y-%m')) -> None:
        self._path, self.cap, self._month = Path(path), cap_usd, month
        self._lock = threading.Lock()

    def _read(self) -> dict[str, float]:
        try:
            doc = json.loads(self._path.read_text(encoding='utf-8'))
            return {k: float(v) for k, v in doc.items()} if isinstance(doc, dict) else {}
        except (OSError, ValueError):
            return {}

    def spent(self) -> float:
        return self._read().get(self._month(), 0.0)

    def allowed(self) -> bool:
        return self.spent() < self.cap

    def add(self, usd: float) -> None:
        with self._lock:
            doc = self._read()
            doc[self._month()] = round(doc.get(self._month(), 0.0) + usd, 6)
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix('.tmp')
            tmp.write_text(json.dumps(doc, indent=1), encoding='utf-8')
            tmp.replace(self._path)


class BudgetedProvider:
    """Claude under the monthly cap: over it, the call is refused as "model unavailable", so the
    line goes to the local model (ADR-0147); every answered call adds its cost."""

    def __init__(self, inner: AnthropicProvider, budget: MonthlyBudget) -> None:
        self._inner, self._budget = inner, budget
        self.model = inner.model

    def generate(self, messages: Sequence[dict[str, str]]) -> str:
        if not self._budget.allowed():
            raise LlmError('claude monthly budget reached')
        try:
            return self._inner.generate(messages)
        finally:
            cost = claude_cost(self.model, self._inner.last_usage)
            if cost:
                self._budget.add(cost)
            self._inner.last_usage = {}


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
