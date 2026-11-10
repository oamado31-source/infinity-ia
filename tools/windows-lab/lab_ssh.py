# SPDX-License-Identifier: Apache-2.0
"""SSH transport for the Windows lab VMs (CR-2026-001 / CR-2026-002). Read-only helpers.

Each VM is addressed by a full ssh command kept in an environment variable, so no user name, key
path or IP lives in the repository, e.g.
  INFINITY_LAB_SSH='ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes -o BatchMode=yes -l "<user>" <vm-ip>'
"""
from __future__ import annotations

import base64
import json
import math
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone

TAIL_BYTES = 65536


def ssh_from_env(var: str) -> list[str]:
    raw = os.environ.get(var)
    if not raw:
        sys.exit(f'set {var} to the ssh command for the lab VM')
    return shlex.split(os.path.expanduser(raw))


def run_ps(ssh: list[str], script: str, timeout: int = 300, stdin: bytes | None = None) -> str:
    """Run a PowerShell script on the VM. Large inputs go through `stdin` as ONE line, read in the
    script with [Console]::In.ReadLine(), because the Windows command line is limited to ~8 KB.
    ReadToEnd() stalls intermittently on this OpenSSH for inputs above ~4 KB (EOF is not seen);
    a newline-terminated single line is read reliably (tested up to 60 KB)."""
    if stdin is not None:
        if b'\n' in stdin.rstrip(b'\n'):
            raise ValueError('stdin must be a single line (JSON or base64)')
        stdin = stdin.rstrip(b'\n') + b'\n'
    script = "$ProgressPreference = 'SilentlyContinue'\n" + script
    encoded = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
    cmd = ssh + [f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded}']
    result = subprocess.run(cmd, capture_output=True, timeout=timeout, input=stdin)
    # The Windows console code page is not UTF-8 (cp850 here); stdout carries ASCII JSON only.
    stderr = result.stderr.decode('cp850', errors='replace')
    if result.returncode != 0:
        raise RuntimeError(f'remote powershell failed: {stderr.strip()[:300]}')
    return result.stdout.decode('utf-8', errors='replace')


class SshLogSource:
    """LogSource over SSH: tail of the loader log as raw bytes (a half-written line stays visible)."""

    def __init__(self, ssh: list[str], game_root: str) -> None:
        self._ssh = ssh
        self._script = f'''
$f = Join-Path '{game_root}' 'InfinityLoader.log'
if (-not (Test-Path -LiteralPath $f)) {{ '{{"exists":false}}'; exit }}
$age = ((Get-Date) - (Get-Item -LiteralPath $f).LastWriteTime).TotalSeconds
$s = [IO.File]::Open($f, 'Open', 'Read', 'ReadWrite')
try {{
  $n = [Math]::Min($s.Length, {TAIL_BYTES}); [void]$s.Seek(-$n, 'End')
  $b = New-Object byte[] $n; [void]$s.Read($b, 0, $n)
}} finally {{ $s.Dispose() }}
@{{exists=$true; age=$age; b64=[Convert]::ToBase64String($b)}} | ConvertTo-Json -Compress
'''

    def fetch(self) -> tuple[str, float]:
        doc = json.loads(run_ps(self._ssh, self._script, timeout=60))
        if not doc.get('exists'):
            return '', math.inf
        text = base64.b64decode(doc['b64']).decode('utf-8', errors='replace')
        return text, float(doc['age'])


def put_override_file(ssh: list[str], game_root: str, name: str, data: bytes) -> None:
    """Write one file into the game copy's override folder (bytes as given), atomically."""
    if not name.replace('.', '').replace('_', '').replace('-', '').isalnum():
        raise ValueError(f'unsafe file name {name!r}')
    run_ps(ssh, f'''
$dir = Join-Path '{game_root}' 'override'
$tmp = Join-Path $dir '{name}.tmp'
[IO.File]::WriteAllBytes($tmp, [Convert]::FromBase64String([Console]::In.ReadLine().Trim()))
Move-Item -LiteralPath $tmp -Destination (Join-Path $dir '{name}') -Force
''', timeout=60, stdin=base64.b64encode(data))


def remove_override_file(ssh: list[str], game_root: str, name: str) -> None:
    if not name.replace('.', '').replace('_', '').replace('-', '').isalnum():
        raise ValueError(f'unsafe file name {name!r}')
    run_ps(ssh, f"Remove-Item -LiteralPath (Join-Path '{game_root}' 'override\\{name}') "
                "-ErrorAction SilentlyContinue", timeout=60)


def live_manifest(ssh: list[str], game_root: str, out_name: str = 'lab-live-manifest.json') -> dict:
    """Run the read-only P0 collector (already copied to the VM home) and return its JSON."""
    out = run_ps(ssh, f'''
& powershell -NoProfile -ExecutionPolicy Bypass -File p0-collect-manifest.ps1 -GameRoot '{game_root}' -OutFile {out_name} | Out-Null
Get-Content -Raw {out_name}
''')
    return json.loads(out)


def grep_log(ssh: list[str], game_root: str, pattern: str, limit: int = 20) -> list[str]:
    """Lines of the loader log matching a regex (case-insensitive), for desync/network checks."""
    out = run_ps(ssh, f'''
$f = Join-Path '{game_root}' 'InfinityLoader.log'
if (Test-Path -LiteralPath $f) {{
  @(Select-String -LiteralPath $f -Pattern '{pattern}' | Select-Object -First {limit} | ForEach-Object {{ $_.Line }}) | ConvertTo-Json -Compress
}} else {{ '[]' }}
''', timeout=60).strip()
    lines = json.loads(out) if out else []
    return [lines] if isinstance(lines, str) else list(lines)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


class SshByteSource:
    """ByteSource over SSH: reads slices of files in the VM's game copy into memory only.

    Nothing from the game is written on this machine (REQ-CANON-004); callers keep the bytes in
    memory and persist only derived, local-only data outside the repository.
    """

    def __init__(self, ssh: list[str], game_root: str, batch: int = 200) -> None:
        self._ssh, self._root, self._batch = ssh, game_root.rstrip('\\'), batch

    def _win(self, path: str) -> str:
        rel = path.replace('/', '\\').lstrip('\\')
        if '..' in rel.split('\\') or "'" in rel:
            raise ValueError(f'unsafe path {path!r}')
        return f'{self._root}\\{rel}'

    def size(self, path: str) -> int | None:
        out = run_ps(self._ssh, f"$f = '{self._win(path)}'; "
                                "if (Test-Path -LiteralPath $f -PathType Leaf) "
                                "{ (Get-Item -LiteralPath $f).Length } else { -1 }", timeout=60)
        value = int(out.strip() or -1)
        return None if value < 0 else value

    def read(self, path: str, offset: int, length: int) -> bytes:
        return self.read_many([(path, offset, length)])[0]

    def read_many(self, requests) -> list[bytes]:
        results: list[bytes] = []
        for start in range(0, len(requests), self._batch):
            chunk = [{'p': self._win(p), 'o': int(o), 'n': int(n)}
                     for p, o, n in requests[start:start + self._batch]]
            out = run_ps(self._ssh, '''
$reqs = [Console]::In.ReadLine() | ConvertFrom-Json
$res = foreach ($r in @($reqs)) {
  $s = [IO.File]::Open($r.p, 'Open', 'Read', 'ReadWrite')
  try {
    [void]$s.Seek([int64]$r.o, 'Begin'); $b = New-Object byte[] ([int]$r.n)
    $got = 0; while ($got -lt $r.n) { $k = $s.Read($b, $got, $r.n - $got); if ($k -le 0) { break }; $got += $k }
    if ($got -ne $r.n) { throw "short read $($r.p)" }
    [Convert]::ToBase64String($b)
  } finally { $s.Dispose() }
}
ConvertTo-Json -Compress -InputObject @($res)
''', timeout=300, stdin=json.dumps(chunk).encode())
            decoded = json.loads(out)
            decoded = [decoded] if isinstance(decoded, str) else decoded
            if len(decoded) != len(chunk):
                raise RuntimeError('remote read returned a different number of slices')
            results.extend(base64.b64decode(item) for item in decoded)
        return results

    def list_dir(self, path: str, suffix: str) -> list[str]:
        out = run_ps(self._ssh, f"$d = '{self._win(path)}'; if (Test-Path -LiteralPath $d) "
                                f"{{ ConvertTo-Json -Compress -InputObject @(Get-ChildItem -LiteralPath $d -File "
                                f"| Where-Object {{ $_.Name -like '*{suffix}' }} | ForEach-Object {{ $_.Name }}) }} "
                                "else { '[]' }", timeout=60).strip()
        names = json.loads(out) if out else []
        return sorted([names] if isinstance(names, str) else names)
