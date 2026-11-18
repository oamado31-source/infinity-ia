# SPDX-License-Identifier: Apache-2.0
"""ADR-0136 / ADR-0137 lab helper: build one of OUR creature files and deploy it (game closed).

BG2:EE's CreateCreature takes no script name, so ownership lives in the file: a CRE of ours (IA*)
whose script-name field holds a name of ours (INFAI_*). Two ways to build it:
- `--copy <CRE>`: a copy of a living CRE of the build (ADR-0136, the P3 test);
- `--from-sheet <sheet.json> --base <CRE> --animation <ANIMATE.IDS symbol>`: a creature of another
  game, from a curated local sheet (ADR-0137): the name comes from a dialog.tlk string that already
  exists, the items from the build's items with the same name, the body colors from the sheet;
  `--vision` adds the vision look (translucent, pale glow) for the campaign's dead.
The bytes are game data (CR-2026-030): they go only to the VM's override and to a local registry
(~/.infinity-ai/templates/install-<build>/templates.json), never to the repository. The engine only
finds override files present at launch: deploy with the game closed, then pin a new manifest.

  python tools/windows-lab/build_templates.py --copy MTOWN6 --as IAP3TEST --name INFAI_P3TEST
  python tools/windows-lab/build_templates.py --from-sheet ~/.infinity-ai/sheets/bg1/tamoko.json \\
      --base MTOWN6 --animation CLERIC_FEMALE_HUMAN --vision --as IATAMOKO --name INFAI_TAMOKO
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infinity_ai.actions.creatures import build_creature, parse_sheet, vision_effects  # noqa: E402
from infinity_ai.actions.gateway import (  # noqa: E402
    TEMPLATES_SCHEMA, ActionError, make_template, templates_path,
)
from infinity_ai.bridge.manifest import build_fingerprint  # noqa: E402
from infinity_ai.gamedata.formats import CRE_TYPE, ITM_TYPE  # noqa: E402
from infinity_ai.gamedata.inventory import _read_located, _Resources  # noqa: E402
from lab_ssh import SshByteSource, live_manifest, put_override_file, run_ps, ssh_from_env  # noqa: E402

IDS_TYPE = 0x3F0


def strrefs_of(source, language: str, names: set[str]) -> dict[str, list[int]]:
    """dialog.tlk entries whose text is exactly one of `names` (read in memory, nothing kept)."""
    path = f'lang/{language}/dialog.tlk'
    data = source.read(path, 0, source.size(path))
    count, base = struct.unpack_from('<II', data, 0x0A)
    out: dict[str, list[int]] = {n: [] for n in names}
    for i in range(count):
        _, _, _, _, start, length = struct.unpack_from('<H8sIIII', data, 18 + 26 * i)
        if 0 < length <= 80:
            text = data[base + start:base + start + length].decode('utf-8', 'replace').strip()
            if text in out:
                out[text].append(i)
    return out


def items_named(source, res: _Resources, strrefs: dict[str, list[int]]) -> dict[str, str]:
    """Item name -> ITM resref of the build whose identified name is that string (first by
    resref, so SHLD06 before SHLD06A)."""
    wanted = {ref: name for name, refs in strrefs.items() for ref in refs}
    located = {r.resref.upper(): loc for r in res.key.of_type(ITM_TYPE)
               if (loc := res.locate(r.resref.upper(), ITM_TYPE, 'itm', set())) is not None}
    found: dict[str, str] = {}
    for ref, head in sorted(_read_located(source, located, limit=0x10).items()):
        if len(head) >= 0x10:
            identified = struct.unpack_from('<I', head, 0x0C)[0]
            name = wanted.get(identified)
            if name and name not in found:
                found[name] = ref
    return found


def animation_id(source, res: _Resources, symbol: str) -> int | None:
    loc = res.locate('ANIMATE', IDS_TYPE, 'ids', set())
    text = _read_located(source, {'ANIMATE': loc})['ANIMATE'].decode('latin-1') if loc else ''
    for line in text.splitlines():
        m = re.match(r'\s*(0x[0-9A-Fa-f]+|\d+)\s+(\S+)', line)
        if m and m.group(2).upper() == symbol.upper():
            return int(m.group(1), 0)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--copy', help='CRE of the build to copy (ADR-0136)')
    ap.add_argument('--from-sheet', type=Path, help='local creature sheet (ADR-0137)')
    ap.add_argument('--base', help='living CRE of the build that gives the body (with --from-sheet)')
    ap.add_argument('--animation', help='ANIMATE.IDS symbol (with --from-sheet)')
    ap.add_argument('--vision', action='store_true',
                    help='translucent with a pale glow (with --from-sheet)')
    ap.add_argument('--as', dest='target', required=True, help='our resref (IA + up to 6)')
    ap.add_argument('--name', required=True, help='our script name (INFAI_...)')
    ap.add_argument('--language', default='pt_BR')
    ap.add_argument('--game-root', default=r'C:\InfinityLab\BG2EE-P1')
    args = ap.parse_args()
    target = args.target.upper()
    if not (target.startswith('IA') and 3 <= len(target) <= 8 and target.isalnum()):
        print('o nome do arquivo precisa ser IA + ate 6 letras ou numeros')
        return 2
    if bool(args.copy) == bool(args.from_sheet):
        print('use --copy ou --from-sheet (um dos dois)')
        return 2
    if args.vision and not args.from_sheet:
        print('--vision so vale com --from-sheet')
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
    base_ref = (args.copy or args.base or '').upper()
    loc = res.locate(base_ref, CRE_TYPE, 'cre', over) if base_ref else None
    if loc is None:
        print(f'{base_ref or "(sem base)"} nao existe nesta build')
        return 2
    base = _read_located(source, {base_ref: loc})[base_ref]
    record = {'resref': target, 'script_name': args.name.upper(), 'source_cre': base_ref,
              'created_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    try:
        if args.copy:
            data = make_template(base, args.name.upper())
            record['kind'] = 'COPY'
        else:
            sheet = parse_sheet(json.loads(args.from_sheet.expanduser().read_text(encoding='utf-8')))
            names = {sheet.name} | {name for _, name in sheet.items}
            strrefs = strrefs_of(source, args.language, names)
            if not strrefs[sheet.name]:
                print(f'recusado: o nome {sheet.name!r} nao existe no dialog.tlk desta build')
                return 2
            animation = animation_id(source, res, args.animation or '')
            if animation is None:
                print(f'recusado: animacao {args.animation!r} nao existe no ANIMATE.IDS')
                return 2
            found = items_named(source, res, {n: strrefs[n] for _, n in sheet.items})
            items = {slot: found[name] for slot, name in sheet.items if name in found}
            for slot, name in sheet.items:
                print(f'item {slot}: {name} -> {found.get(name, "NAO ACHADO (fica de fora)")}')
            print('cores:', 'as da base' if sheet.colors is None else list(sheet.colors))
            effects = vision_effects() if args.vision else ()
            data = build_creature(base, sheet, script_name=args.name.upper(),
                                  name_strref=strrefs[sheet.name][0], animation=animation,
                                  items=items, effects=effects)
            record.update(kind='SHEET', sheet_id=sheet.sheet_id, name_strref=strrefs[sheet.name][0],
                          animation=args.animation.upper(), items=items,
                          colors=list(sheet.colors) if sheet.colors else None,
                          vision=args.vision)
    except ActionError as exc:
        print(f'recusado: {exc.code}')
        return 2
    put_override_file(ssh, args.game_root, f'{target}.CRE', data)
    fingerprint = build_fingerprint(live_manifest(ssh, args.game_root, 'templates-manifest.json'))
    path = templates_path(fingerprint)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {'schema': TEMPLATES_SCHEMA, 'build_fingerprint': fingerprint, 'templates': []}
    if path.is_file():
        old = json.loads(path.read_text(encoding='utf-8'))
        if old.get('build_fingerprint') == fingerprint:
            doc['templates'] = [t for t in old.get('templates', []) if t['resref'] != target]
    doc['templates'].append(record)
    path.write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
    print(f'instalado: override\\{target}.CRE ({record["kind"]} de {base_ref}, nome {args.name.upper()})')
    print(f'registro local: {path}')
    print('o arquivo muda o hash dos mods: fixe um manifesto novo antes de reabrir o jogo')
    return 0


if __name__ == '__main__':
    sys.exit(main())
