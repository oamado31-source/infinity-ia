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


def run_ps(ssh: list[str], script: str, timeout: int = 300) -> str:
    script = "$ProgressPreference = 'SilentlyContinue'\n" + script
    encoded = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
    cmd = ssh + [f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded}']
    result = subprocess.run(cmd, capture_output=True, timeout=timeout)
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
