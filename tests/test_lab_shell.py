# SPDX-License-Identifier: Apache-2.0
"""S1i latency: the long-lived remote shell and the incremental log tail (no VM; a local stand-in
answers the same one-line protocol)."""
import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'windows-lab'))

from lab_ssh import RemoteShell, RemoteShellError, SshLogSource  # noqa: E402

# Stands in for "ssh <vm> powershell ... -EncodedCommand <loop>": reads one request per line and
# answers "@@INFAI <ok> <base64>". The "script" is Python here: an expression over `stdin`.
STAND_IN = r'''
import base64, sys, time
print('banner que deve ser ignorado', flush=True)
for line in sys.stdin:
    code, _, stdin = line.rstrip('\n').partition(' ')
    script = base64.b64decode(code).decode()
    if script == 'hang':
        time.sleep(30)
    try:
        out, ok = str(eval(script, {'stdin': stdin, 'state': STATE})), 1
    except Exception as exc:
        out, ok = str(exc), 0
    print('@@INFAI', ok, base64.b64encode(out.encode()).decode(), flush=True)
'''


class RemoteShellTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        script = Path(self.dir.name) / 'stand_in.py'
        script.write_text('STATE = {}\n' + STAND_IN, encoding='utf-8')
        # RemoteShell appends "-o ServerAliveInterval=15 <powershell command>": swallowed here.
        self.cmd = [sys.executable, '-c',
                    f'import sys; sys.argv = sys.argv[:1]; exec(open({str(script)!r}).read())']

    def tearDown(self):
        self.dir.cleanup()

    def test_calls_reuse_one_session_and_carry_stdin(self):
        shell = RemoteShell(self.cmd)
        try:
            self.assertEqual(shell.run('1 + 1'), '2')
            first = shell._proc
            self.assertEqual(shell.run('len(stdin)', stdin=b'YWJj'), '4')
            self.assertIs(shell._proc, first)                 # no new login per call
            with self.assertRaises(ValueError):
                shell.run('1', stdin=b'com espaco')
        finally:
            shell.close()

    def test_errors_and_timeouts(self):
        shell = RemoteShell(self.cmd, timeout=1.0)
        try:
            with self.assertRaises(RemoteShellError):
                shell.run('1 / 0')                            # script error: session stays
            self.assertEqual(shell.run('3'), '3')
            with self.assertRaises(RemoteShellError):
                shell.run('hang')                             # too slow: session is killed
            self.assertIsNone(shell._proc)
            self.assertEqual(shell.run('4'), '4')             # and started again
        finally:
            shell.close()


class FakeShell:
    """Answers the log script like the VM would: the tail only when the length changed."""

    def __init__(self) -> None:
        self.log = b'linha 1\n'
        self.sent_tails = 0

    def run(self, script: str, stdin=None, timeout=None) -> str:
        known = int(script.split('$len -eq ')[1].split(')')[0])
        doc = {'exists': True, 'age': 0.5, 'len': len(self.log), 'b64': None}
        if len(self.log) != known:
            doc['b64'] = base64.b64encode(self.log).decode()
            self.sent_tails += 1
        return json.dumps(doc)


class LogTailTests(unittest.TestCase):
    def test_unchanged_log_is_not_sent_again(self):
        shell = FakeShell()
        source = SshLogSource(None, r'C:\Jogo', shell=shell, full_every=60)
        text, _ = source.fetch()
        self.assertEqual(text, 'linha 1\n')
        again, _ = source.fetch()
        self.assertIs(again, text)                            # same copy: nothing re-parsed
        self.assertEqual(shell.sent_tails, 1)
        shell.log += b'linha 2\n'
        self.assertEqual(source.fetch()[0], 'linha 1\nlinha 2\n')
        self.assertEqual(shell.sent_tails, 2)


if __name__ == '__main__':
    unittest.main()
