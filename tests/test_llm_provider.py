# SPDX-License-Identifier: Apache-2.0
"""The Ollama request (S1h/S1i) and the Claude request (ADR-0147)."""
import io
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.dialogue.llm import (AnthropicProvider, LlmError, OllamaProvider,  # noqa: E402
                                      claude_cost)


class OllamaRequestTests(unittest.TestCase):
    def test_request_bounds_context_and_keeps_the_model_loaded(self):
        sent = {}

        def fake_urlopen(request, timeout):
            sent.update(json.loads(request.data))
            reply = {'message': {'content': '{"speech": "Oi.", "used_facts": [], "unknown": false}'}}
            return io.BytesIO(json.dumps(reply).encode())

        with mock.patch('urllib.request.urlopen', fake_urlopen):
            OllamaProvider().generate([{'role': 'user', 'content': 'Oi'}])
        self.assertEqual(sent['options']['num_ctx'], 8192)
        self.assertEqual(sent['keep_alive'], '30m')
        self.assertEqual(sent['model'], 'qwen3:30b-a3b')


REPLY = '{"speech": "Oi.", "used_facts": [], "unknown": false}'


class FakeMessages:
    def __init__(self, outcome):
        self.outcome, self.sent = outcome, []

    def create(self, **kw):
        self.sent.append(kw)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def reply(text=REPLY, stop='end_turn', **usage):
    usage = {'input_tokens': 100, 'output_tokens': 20, 'cache_read_input_tokens': 0,
             'cache_creation_input_tokens': 0, **usage}
    return SimpleNamespace(stop_reason=stop, usage=SimpleNamespace(**usage),
                           content=[SimpleNamespace(type='text', text=text)])


def claude(outcome):
    messages = FakeMessages(outcome)
    return AnthropicProvider(client=SimpleNamespace(messages=messages)), messages


class ClaudeRequestTests(unittest.TestCase):
    def test_rules_become_the_cached_system_prompt_and_hints_stay_in_place(self):
        provider, api = claude(reply())
        text = provider.generate([{'role': 'system', 'content': 'REGRAS'},
                                  {'role': 'user', 'content': 'Oi'},
                                  {'role': 'system', 'content': 'DICA'}])
        self.assertEqual(text, REPLY)
        sent = api.sent[0]
        self.assertEqual(sent['model'], 'claude-haiku-5-5')
        self.assertEqual(sent['system'], [{'type': 'text', 'text': 'REGRAS',
                                           'cache_control': {'type': 'ephemeral'}}])
        self.assertEqual(sent['messages'], [{'role': 'user', 'content': 'Oi'},
                                            {'role': 'system', 'content': 'DICA'}])

    def test_fast_line_with_the_reply_json_enforced(self):
        provider, api = claude(reply())
        provider.generate([{'role': 'user', 'content': 'Oi'}])
        sent = api.sent[0]
        self.assertEqual(sent['thinking'], {'type': 'disabled'})
        self.assertEqual(sent['output_config']['effort'], 'low')
        schema = sent['output_config']['format']['schema']
        self.assertEqual(sent['output_config']['format']['type'], 'json_schema')
        self.assertIs(schema['additionalProperties'], False)
        self.assertEqual(schema['required'], ['speech', 'used_facts', 'unknown'])
        self.assertNotIn('temperature', sent)    # Haiku 5.5 rejects sampling parameters

    def test_any_failure_is_model_unavailable(self):
        provider, _ = claude(RuntimeError('no key'))
        with self.assertRaises(LlmError):
            provider.generate([{'role': 'user', 'content': 'Oi'}])
        for bad in (reply(stop='refusal'), reply(text='  ')):
            provider, _ = claude(bad)
            with self.assertRaises(LlmError):
                provider.generate([{'role': 'user', 'content': 'Oi'}])

    def test_usage_adds_up_and_has_a_cost(self):
        provider, _ = claude(reply(cache_read_input_tokens=1000))
        provider.generate([{'role': 'user', 'content': 'Oi'}])
        provider.generate([{'role': 'user', 'content': 'Oi'}])
        self.assertEqual(provider.requests, 2)
        self.assertEqual(provider.usage_total['input_tokens'], 200)
        self.assertEqual(provider.usage_total['cache_read_input_tokens'], 2000)
        cost = claude_cost('claude-haiku-5-5', provider.usage_total)
        self.assertAlmostEqual(cost, (200 * 0.10 + 40 * 0.50 + 2000 * 0.01) / 1_000_000)
        self.assertIsNone(claude_cost('outro', provider.usage_total))


if __name__ == '__main__':
    unittest.main()
