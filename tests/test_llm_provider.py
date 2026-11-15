# SPDX-License-Identifier: Apache-2.0
"""The Ollama request: bounded context and a model kept loaded between talks (S1h/S1i)."""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.dialogue.llm import OllamaProvider  # noqa: E402


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


if __name__ == '__main__':
    unittest.main()
