# SPDX-License-Identifier: Apache-2.0
"""ADR-0136 lab helper: build one of OUR creature files and deploy it (game closed).

BG2:EE's CreateCreature takes no script name, so ownership lives in the file: a copy of a CRE of
the build, under a resref of ours (IA*), whose script-name field holds a name of ours (INFAI_*).
The bytes are game data (CR-2026-030): they go only to the VM's override and to a local registry
(~/.infinity-ai/templates/install-<build>/templates.json), never to the repository. The engine
only finds override files present at launch: deploy with the game closed, then pin a new manifest.

  python tools/windows-lab/build_templates.py --copy DPMALE --as IAP3TEST --name INFAI_P3TEST
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.actions.gateway import (  # noqa: E402
    TEMPLATES_SCHEMA, ActionError, make_template, templates_path,
)
from infinity_ai.bridge.manifest import build_fingerprint  # noqa: E402
from infinity_ai.gamedata.formats import CRE_TYPE  # noqa: E402
from infinity_ai.gamedata.inventory import _read_located, _Resources  # noqa: E402
from lab_ssh import SshByteSource, live_manifest, put_override_file, run_ps, ssh_from_env  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--copy', required=True, help='CRE of the build to copy')
    ap.add_argument('--as', dest='target', required=True, help='our resref (IA + up to 6)')
    ap.add_argument('--name', required=True, help='our script name (INFAI_...)')
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    args = ap.parse_args()
    target = args.target.upper()
    if not (target.startswith('IA') and 3 <= len(target) <= 8 and target.isalnum()):
        print('o nome do arquivo precisa ser IA + ate 6 letras ou numeros')
        return 2
    ssh = ssh_from_env('INFINITY_LAB_SSH')
    running = run_ps(ssh, "(Get-Process -Name Baldur,InfinityLoader -ErrorAction SilentlyContinue"
                          " | Measure-Object).Count", timeout=60).strip()
    if running != '0':
        print('feche o jogo antes: o motor so acha arquivos do override presentes na abertura')
        return 2
    source = SshByteSource(ssh, args.game_root)
    res = _Resources(source)
    over = {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', '.cre')}
    loc = res.locate(args.copy.upper(), CRE_TYPE, 'cre', over)
    if loc is None:
        print(f'{args.copy} nao existe nesta build')
        return 2
    data = _read_located(source, {args.copy.upper(): loc})[args.copy.upper()]
    try:
        template = make_template(data, args.name.upper())
    except ActionError as exc:
        print(f'recusado: {exc.code}')
        return 2
    put_override_file(ssh, args.game_root, f'{target}.CRE', template)
    fingerprint = build_fingerprint(live_manifest(ssh, args.game_root, 'templates-manifest.json'))
    path = templates_path(fingerprint)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {'schema': TEMPLATES_SCHEMA, 'build_fingerprint': fingerprint, 'templates': []}
    if path.is_file():
        old = json.loads(path.read_text(encoding='utf-8'))
        if old.get('build_fingerprint') == fingerprint:
            doc['templates'] = [t for t in old.get('templates', []) if t['resref'] != target]
    doc['templates'].append({
        'resref': target, 'script_name': args.name.upper(), 'source_cre': args.copy.upper(),
        'kind': 'COPY', 'created_at': datetime.now(timezone.utc).isoformat(timespec='seconds')})
    path.write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
    print(f'instalado: override\\{target}.CRE (copia de {args.copy.upper()}, nome {args.name.upper()})')
    print(f'registro local: {path}')
    print('o arquivo muda o hash dos mods: fixe um manifesto novo antes de reabrir o jogo')
    return 0


if __name__ == '__main__':
    sys.exit(main())
