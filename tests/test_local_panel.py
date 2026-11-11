# SPDX-License-Identifier: Apache-2.0
"""Safety and route tests for the loopback-only Infinity AI development panel."""
from __future__ import annotations

import importlib.util
import json
import socket
import sqlite3
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "local-panel" / "server.py"
SPEC = importlib.util.spec_from_file_location("infinity_local_panel", SOURCE)
panel = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = panel
SPEC.loader.exec_module(panel)


class ValidationTests(unittest.TestCase):
    def test_branch_whitelist_rejects_ref_injection_and_unsafe_names(self):
        for value in ("main", "feat/adr-0120", "docs/foo_bar", "fix/v1.2"):
            self.assertTrue(panel.valid_branch(value), value)
        for value in ("--force", "-x", "../main", "a..b", "a//b",
                      "@{1}", "refs/.hidden", "a.lock", "foo/", "HEAD",
                      "main;rm -rf /", "foo\nbar", "", None):
            self.assertFalse(panel.valid_branch(value), value)

    def test_campaign_whitelist_prevents_path_escape(self):
        for value in ("lab-s1f", "lab-s1g", "lab-abc-01"):
            self.assertTrue(panel.valid_campaign(value))
        for value in ("real", "lab-../secrets", "lab-X", "lab-", "lab-a/b", "lab-foo;sh"):
            self.assertFalse(panel.valid_campaign(value))

    def test_config_whitelist_and_no_arbitrary_ssh_command(self):
        accepted = panel.settings_validate({
            "campaign": "lab-s1f", "model": "qwen3:8b",
            "ssh_host": "labvm", "ssh_user": "otavio amado", "ssh_key": "~/.ssh/id_ed25519",
        })
        self.assertTrue(accepted["ssh_key"].endswith(".ssh/id_ed25519"))
        for bad in (
            {"campaign": "my-real-campaign"},
            {"ssh_host": "labvm; echo compromised"},
            {"ssh_host": "-oProxyCommand=sh"},
            {"ssh_user": "a;whoami", "ssh_host": "labvm"},
            {"ssh_key": "~/.ssh/key", "ssh_host": ""},
            {"model": "model\ncommand"},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                panel.settings_validate(bad)

    def test_allowed_actions_do_not_accept_shell_commands(self):
        manager = panel.Panel()
        with self.assertRaisesRegex(ValueError, "não autorizada"):
            manager.job_commands("run", {"command": "touch ~/.bad"})
        label, commands = manager.job_commands("all", {})
        self.assertTrue(label)
        self.assertEqual(len(commands), 6)
        self.assertTrue(all(isinstance(c, list) and len(c) >= 2 for c in commands))
        self.assertTrue(all("--shell" not in c for c in commands))

    def test_lab_preflight_rejects_occupied_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as owner:
            owner.bind(("127.0.0.1", 0))
            owner.listen()
            with self.assertRaisesRegex(ValueError, "já ocupada"):
                panel.check_lab_port("127.0.0.1", owner.getsockname()[1])

    def test_lab_bind_failure_is_checked_before_vm_override(self):
        source = (ROOT / "tools" / "windows-lab" /
                  "dialogue_service.py").read_text(encoding="utf-8")
        main = source.split("\ndef main() -> int:", 1)[1]
        self.assertLess(main.index("if not matches:"),
                        main.index("server = ThreadingHTTPServer"))
        self.assertLess(main.index("server = ThreadingHTTPServer"),
                        main.index("put_override_file("))
        self.assertLess(main.index("server = ThreadingHTTPServer"),
                        main.index("observer.start()"))

    def test_pin_requires_running_matching_laboratory(self):
        manager = panel.Panel()
        with self.assertRaisesRegex(ValueError, "Inicie o serviço"):
            manager.job_commands("pin", {})

    def test_empty_campaign_cannot_get_pin_without_game_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "lab.sqlite3"
            with self.assertRaises(ValueError):
                panel.checked_game_time(db, "lab-s1f")
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE campaigns (campaign_id TEXT)")
                conn.execute("CREATE TABLE events (game_time INTEGER)")
                conn.execute("INSERT INTO campaigns VALUES ('lab-s1f')")
            with self.assertRaises(ValueError):
                panel.checked_game_time(db, "lab-s1f")
            with sqlite3.connect(db) as conn:
                conn.execute("INSERT INTO events VALUES (136900)")
            self.assertEqual(panel.checked_game_time(db, "lab-s1f"), 136900)
            with self.assertRaises(ValueError):
                panel.checked_game_time(db, "lab-other")

    def test_job_logs_remain_accessible_after_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            logs = base / "logs"
            logs.mkdir()
            ident = "a" * 16
            (logs / ("job-" + ident + ".log")).write_text(
                "[2026-11-10T20:00:00+00:00] Testes de identidade\n"
                "$ python -m unittest discover\n"
                "Ran 42 tests\n"
                "[2026-11-10T20:00:03+00:00] Finalizado: código 0\n",
                encoding="utf-8",
            )
            with mock.patch.multiple(panel, DATA=base, LOGS=logs,
                                     CONFIG_PATH=base / "config.json"):
                restarted = panel.Panel()
                job = restarted.jobs[ident]
                self.assertEqual(job.status, "ok")
                self.assertEqual(job.label, "Testes de identidade")
                self.assertEqual(job.code, 0)

    def test_settings_are_stored_only_outside_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with mock.patch.multiple(panel, DATA=base, LOGS=base / "logs",
                                     CONFIG_PATH=base / "config.json"):
                saved = panel.write_settings({
                    "campaign": "lab-test", "model": "qwen3:8b",
                    "manifest": "/tmp/test.json", "ssh_host": "vm.local",
                })
                self.assertEqual(saved["campaign"], "lab-test")
                self.assertEqual(panel.read_settings()["ssh_host"], "vm.local")
                self.assertFalse(str(panel.CONFIG_PATH).startswith(str(ROOT)))
                self.assertEqual(panel.CONFIG_PATH.stat().st_mode & 0o777, 0o600)


class LocalHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.patch = mock.patch.multiple(
            panel, DATA=Path(cls.temp.name), LOGS=Path(cls.temp.name) / "logs",
            CONFIG_PATH=Path(cls.temp.name) / "config.json")
        cls.patch.start()
        cls.manager = panel.Panel()
        cls.server = panel.Server(0, cls.manager)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=3)
        cls.patch.stop()
        cls.temp.cleanup()

    def request(self, path, *, method="GET", data=None, token=False, origin=None,
                host=None):
        headers = {}
        if token:
            headers["X-Panel-Token"] = self.manager.token
        if origin is not None:
            headers["Origin"] = origin
        if host is not None:
            headers["Host"] = host
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = Request(
            self.base + path,
            data=(json.dumps(data).encode("utf-8") if data is not None else None),
            headers=headers, method=method,
        )
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            try:
                return error.code, error.read().decode("utf-8")
            finally:
                error.close()

    def test_main_page_and_static_assets(self):
        code, html = self.request("/")
        self.assertEqual(code, 200)
        self.assertIn("INFINITY AI", html)
        self.assertIn(self.manager.token, html)
        self.assertNotIn("__TOKEN_JSON__", html)
        code, js = self.request("/static/app.js")
        self.assertEqual(code, 200)
        self.assertIn("runAction", js)

    def test_api_reads_require_token(self):
        code, _ = self.request("/api/status")
        self.assertEqual(code, 403)
        code, body = self.request("/api/status", token=True)
        self.assertEqual(code, 200)
        payload = json.loads(body)
        self.assertTrue(payload["ok"])
        self.assertIn("repo", payload)
        code, _ = self.request("/api/log?kind=service")
        self.assertEqual(code, 403)

    def test_post_token_required_and_cross_site_origin_rejected(self):
        code, _ = self.request("/api/config", method="POST", data={"campaign": "lab-s1f"})
        self.assertEqual(code, 403)
        code, _ = self.request("/api/config", method="POST",
                               data={"campaign": "lab-s1f"}, token=True,
                               origin="https://unrelated.example")
        self.assertEqual(code, 403)

    def test_dns_rebinding_host_rejected(self):
        code, _ = self.request("/api/status", token=True, host="another.example:9999")
        self.assertEqual(code, 403)

    def test_unknown_command_is_not_executed(self):
        code, body = self.request("/api/action", method="POST",
                                  data={"action": "shell", "command": "touch /tmp/pwned"},
                                  token=True)
        self.assertEqual(code, 400)
        self.assertIn("não autorizada", body)
        self.assertIsNone(self.manager.active)

    def test_pin_requires_explicit_confirmation(self):
        code, body = self.request("/api/action", method="POST",
                                  data={"action": "pin"}, token=True)
        self.assertEqual(code, 400)
        self.assertIn("Confirme", body)

    def test_log_path_cannot_escape_log_directory(self):
        code, _ = self.request("/api/log?kind=job&id=../../etc/passwd", token=True)
        self.assertEqual(code, 400)


if __name__ == "__main__":
    unittest.main()
