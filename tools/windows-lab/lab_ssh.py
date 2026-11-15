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
import queue
import shlex
import subprocess
import sys
import threading
import time
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


class RemoteShellError(RuntimeError):
    pass


class RemoteShell:
    """One long-lived PowerShell over one SSH connection (S1i latency). A call costs one round trip
    (~0.1 s on the lab network) instead of an SSH login plus a PowerShell start (~2 s each time).
    Requests are one line each: base64 of the UTF-8 script, then optionally a space and one stdin
    line the script reads as $__stdin. Replies are one line too: "@@INFAI <ok> <base64 output>".
    Errors stop the script (ErrorActionPreference Stop) and come back as ok=0. A broken or slow
    session is killed and started again on the next call. The loop reads PowerShell's own $input:
    [Console]::In.ReadLine() stops receiving after two lines on this Windows OpenSSH."""

    MARK = '@@INFAI'
    LOOP = r"""
$ProgressPreference = 'SilentlyContinue'
$utf8 = New-Object Text.UTF8Encoding $false
foreach ($line in $input) {
  $cut = $line.IndexOf(' ')
  if ($cut -lt 0) { $code = $line; $__stdin = $null }
  else { $code = $line.Substring(0, $cut); $__stdin = $line.Substring($cut + 1) }
  try {
    $ErrorActionPreference = 'Stop'
    $script = $utf8.GetString([Convert]::FromBase64String($code))
    $out = (& ([scriptblock]::Create($script)) | Out-String)
    $ok = 1
  } catch { $out = $_.Exception.Message; $ok = 0 }
  [Console]::Out.WriteLine('@@INFAI ' + $ok + ' ' + [Convert]::ToBase64String($utf8.GetBytes([string]$out)))
  [Console]::Out.Flush()
}
"""

    def __init__(self, ssh: list[str], *, timeout: float = 20.0) -> None:
        self._ssh, self._timeout = ssh, timeout
        self._proc: subprocess.Popen | None = None
        self._lines: queue.Queue[bytes | None] = queue.Queue()
        self._lock = threading.Lock()

    def _start(self) -> None:
        encoded = base64.b64encode(self.LOOP.encode('utf-16-le')).decode('ascii')
        self._proc = subprocess.Popen(
            self._ssh + ['-o', 'ServerAliveInterval=15',
                         f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded}'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self._lines = queue.Queue()
        threading.Thread(target=self._read, args=(self._proc, self._lines), daemon=True).start()

    @staticmethod
    def _read(proc: subprocess.Popen, lines: queue.Queue) -> None:
        for raw in proc.stdout:
            lines.put(raw)
        lines.put(None)

    def close(self) -> None:
        proc, self._proc = self._proc, None
        if proc is not None:
            proc.kill()
            proc.wait()
            for pipe in (proc.stdin, proc.stdout):
                try:
                    pipe.close()
                except OSError:
                    pass

    def run(self, script: str, stdin: bytes | None = None, timeout: float | None = None) -> str:
        if stdin is not None and (b'\n' in stdin.strip() or b' ' in stdin.strip()):
            raise ValueError('stdin must be one line without spaces (base64 or compact JSON)')
        message = base64.b64encode(script.encode('utf-8'))
        if stdin is not None:
            message += b' ' + stdin.strip()
        with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                self._start()
            end = time.monotonic() + (timeout or self._timeout)
            try:
                self._proc.stdin.write(message + b'\n')
                self._proc.stdin.flush()
                while True:
                    raw = self._lines.get(timeout=max(0.0, end - time.monotonic()))
                    if raw is None:
                        raise RemoteShellError('remote shell closed')
                    line = raw.decode('ascii', errors='replace').strip()
                    if line.startswith(self.MARK + ' '):
                        break                       # anything else (banners) is ignored
            except (OSError, queue.Empty, RemoteShellError) as exc:
                self.close()
                raise RemoteShellError(f'remote shell failed: {type(exc).__name__}') from exc
        fields = line.split(' ', 2)
        out = base64.b64decode(fields[2]).decode('utf-8', errors='replace') \
            if len(fields) > 2 else ''
        if fields[1] != '1':
            raise RemoteShellError(f'remote script failed: {out.strip()[:300]}')
        return out


def _run(ssh: list[str] | None, shell: RemoteShell | None, script: str,
         stdin: bytes | None = None, timeout: int = 60) -> str:
    """Through the long-lived shell when there is one, else a one-off SSH + PowerShell."""
    if shell is not None:
        return shell.run(script, stdin, timeout=timeout)
    if stdin is not None:
        script = '$__stdin = [Console]::In.ReadLine()\n' + script
    return run_ps(ssh, script, timeout=timeout, stdin=stdin)


class SshLogSource:
    """LogSource over SSH: tail of the loader log as raw bytes (a half-written line stays visible).
    With a RemoteShell, a poll where the log did not grow costs a few bytes: the tail is sent
    again only when the length changed (and at least every `full_every` seconds)."""

    def __init__(self, ssh: list[str] | None, game_root: str, *, shell: RemoteShell | None = None,
                 full_every: float = 5.0) -> None:
        self._ssh, self._root, self._shell, self._full_every = ssh, game_root, shell, full_every
        self._known: tuple[int, str] | None = None      # (length, text) of the last full read
        self._full_at = 0.0
        # The game process start (UTC ticks), read on full reads: tells game launches apart, since
        # the box's session counter restarts at 0 and the log file is truncated, not recreated.
        self.launch = ''

    def _script(self, known: int) -> str:
        return f"""
$f = Join-Path '{self._root}' 'InfinityLoader.log'
if (-not (Test-Path -LiteralPath $f)) {{ '{{"exists":false}}' }} else {{
  $age = ((Get-Date) - (Get-Item -LiteralPath $f).LastWriteTime).TotalSeconds
  $s = [IO.File]::Open($f, 'Open', 'Read', 'ReadWrite')
  try {{
    $len = $s.Length
    if ($len -eq {known}) {{ $b64 = $null }} else {{
      $n = [Math]::Min($len, {TAIL_BYTES}); [void]$s.Seek(-$n, 'End')
      $b = New-Object byte[] $n; [void]$s.Read($b, 0, $n); $b64 = [Convert]::ToBase64String($b)
    }}
  }} finally {{ $s.Dispose() }}
  $launch = $null
  if ({known} -lt 0) {{
    $p = Get-Process -Name Baldur -ErrorAction SilentlyContinue |
      Where-Object {{ $_.Path -like (Join-Path '{self._root}' '*') }} | Select-Object -First 1
    if ($p) {{ $launch = [string]$p.StartTime.ToUniversalTime().Ticks }}
  }}
  @{{exists=$true; age=$age; len=$len; b64=$b64; launch=$launch}} | ConvertTo-Json -Compress
}}
"""

    def fetch(self) -> tuple[str, float]:
        now = time.monotonic()
        known = self._known[0] if self._known and now - self._full_at < self._full_every else -1
        doc = json.loads(_run(self._ssh, self._shell, self._script(known)))
        if doc.get('launch'):
            self.launch = str(doc['launch'])
        if not doc.get('exists'):
            self._known = None
            return '', math.inf
        if doc.get('b64') is None and self._known is not None:
            return self._known[1], float(doc['age'])
        text = base64.b64decode(doc.get('b64') or '').decode('utf-8', errors='replace')
        self._known, self._full_at = (int(doc.get('len', -1)), text), now
        return text, float(doc['age'])


def put_override_file(ssh: list[str] | None, game_root: str, name: str, data: bytes, *,
                      shell: RemoteShell | None = None) -> None:
    """Write one file into the game copy's override folder (bytes as given), atomically."""
    if not name.replace('.', '').replace('_', '').replace('-', '').isalnum():
        raise ValueError(f'unsafe file name {name!r}')
    _run(ssh, shell, f"""
$dir = Join-Path '{game_root}' 'override'
$tmp = Join-Path $dir '{name}.tmp'
[IO.File]::WriteAllBytes($tmp, [Convert]::FromBase64String($__stdin.Trim()))
Move-Item -LiteralPath $tmp -Destination (Join-Path $dir '{name}') -Force
""", stdin=base64.b64encode(data))


class OverrideWriter:
    """put_override_file through its own long-lived shell, so writes never wait for a log poll."""

    def __init__(self, ssh: list[str], game_root: str) -> None:
        self._ssh, self._root = ssh, game_root
        self._shell = RemoteShell(ssh)

    def put(self, name: str, data: bytes) -> None:
        try:
            put_override_file(self._ssh, self._root, name, data, shell=self._shell)
        except RemoteShellError:
            put_override_file(self._ssh, self._root, name, data)    # one-off SSH as a fallback


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
