# SPDX-License-Identifier: Apache-2.0
"""SPEC-012 (CR-2026-030): census of the people and creatures the game places in its areas.

Read-only, from the local install, into a catalog kept outside the repository: who stands where
(area, position, hours), with which dialogue, whether a store opens from it, and the identity bytes
of the creature. Characters (a humanoid with a name and a script name or a dialogue, or anyone with a
name, a script name and a dialogue) are told apart from creatures without a proper name, which
belong to category 02 later. Deterministic: two runs
on the same install write the same catalog, except the timestamp.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .formats import (
    AREA_TYPE, CRE_IDENTITY_SIZE, CRE_TYPE, DLG_TYPE, parse_are_actors, parse_cre_dialog,
    parse_cre_identity, parse_dlg_store_refs,
)
from .inventory import (
    DEFAULT_LOCAL_DIR as _KNOWLEDGE_DIR, REPO_ROOT, _install_dir, _read_located, _Resources,
    resident_id_for_cre, resolve_strings,
)
from .source import ByteSource, GameDataError

CENSUS_SCHEMA = 'infinity-ai.encyclopedia-census.v1'
DEFAULT_CENSUS_DIR = _KNOWLEDGE_DIR.parent / 'encyclopedia'
CHARACTER, CREATURE = 'CHARACTER', 'CREATURE'
HUMANOID = 1                        # GENERAL.IDS


@dataclass(frozen=True)
class Appearance:
    area: str
    x: int
    y: int
    hours: tuple[int, ...]          # empty = no hour set in the area file


@dataclass(frozen=True)
class CensusEntry:
    entry_id: str                   # npc:<script> or npc:cre-<resref>; embedded: area#actor
    kind: str                       # CHARACTER or CREATURE
    display_name: str | None
    cre_resref: str
    script_name: str
    dialog: str
    sells: bool
    appearances: tuple[Appearance, ...]
    general: int
    race: int
    klass: int
    gender: int
    alignment: int
    allegiance: int


@dataclass(frozen=True)
class Census:
    build_fingerprint: str
    language: str
    entries: tuple[CensusEntry, ...]
    areas: tuple[str, ...]
    generated_at: str

    def characters(self) -> tuple[CensusEntry, ...]:
        return tuple(e for e in self.entries if e.kind == CHARACTER)


def _hours(schedule: int) -> tuple[int, ...]:
    return tuple(h for h in range(24) if schedule & (1 << h))


def build_census(source: ByteSource, *, language: str, build_fingerprint: str,
                 areas: set[str] | frozenset[str] | None = None,
                 now: str | None = None) -> Census:
    """Every actor of every area (or of `areas`), grouped by who it is."""
    resources = _Resources(source)
    over_are = {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', '.are')}
    over_cre = {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', '.cre')}
    over_dlg = {n.rsplit('.', 1)[0].upper() for n in source.list_dir('override', '.dlg')}
    known = {r.resref.upper() for r in resources.key.of_type(AREA_TYPE)} | over_are
    wanted = sorted(known if areas is None else {a.upper() for a in areas} & known)
    located = {a: loc for a in wanted
               if (loc := resources.locate(a, AREA_TYPE, 'are', over_are)) is not None}
    are_data = _read_located(source, located)

    placed: dict[str, list[Appearance]] = {}
    embedded: dict[str, bytes] = {}
    for area in sorted(are_data):
        try:
            actors = parse_are_actors(are_data[area])
        except GameDataError:
            continue
        for actor in actors:
            if actor.embedded is not None:
                key = f'{area}#{actor.actor_name}'
                embedded[key] = actor.embedded
            elif actor.cre_resref:
                key = actor.cre_resref.upper()
            else:
                continue
            placed.setdefault(key, []).append(
                Appearance(area, actor.x, actor.y, _hours(actor.schedule)))
    cre_located = {c: loc for c in placed if c not in embedded
                   if (loc := resources.locate(c, CRE_TYPE, 'cre', over_cre)) is not None}
    cre_data = _read_located(source, cre_located, limit=CRE_IDENTITY_SIZE)
    cre_data.update(embedded)

    identities, dialogs = {}, {}
    for key, data in cre_data.items():
        try:
            identities[key] = parse_cre_identity(data)
            dialogs[key] = parse_cre_dialog(data).upper()
        except GameDataError:
            continue
    dlg_located = {d: loc for d in sorted({d for d in dialogs.values() if d})
                   if (loc := resources.locate(d, DLG_TYPE, 'dlg', over_dlg)) is not None}
    sells = {}
    for ref, data in _read_located(source, dlg_located).items():
        try:
            sells[ref] = bool(parse_dlg_store_refs(data))
        except GameDataError:
            sells[ref] = False
    strings = resolve_strings(source, f'lang/{language}/dialog.tlk',
                              {i.name_strref for i in identities.values()
                               if i.name_strref is not None})

    by_id: dict[str, CensusEntry] = {}
    for key in sorted(identities):
        ident = identities[key]
        if ident.script_name:
            entry_id = f'npc:{ident.script_name.lower()}'
        elif '#' not in key:
            entry_id = resident_id_for_cre(key)
        else:
            entry_id = key.lower()
        name = strings.get(ident.name_strref) if ident.name_strref is not None else None
        dialog = dialogs.get(key, '')
        has_dialog = bool(dialog) and dialog in dlg_located
        # A humanoid with a name and a script name or a dialogue is someone; so is anyone with a
        # name, a script name and a dialogue of its own (SPEC-012 §4.1: individual antagonists).
        is_character = bool(name) and (
            (ident.general == HUMANOID and (bool(ident.script_name) or has_dialog))
            or (bool(ident.script_name) and has_dialog))
        prev = by_id.get(entry_id)
        seen = sorted(set((prev.appearances if prev else ()) + tuple(placed.get(key, ()))),
                      key=lambda a: (a.area, a.x, a.y, a.hours))
        by_id[entry_id] = CensusEntry(
            entry_id, CHARACTER if is_character or (prev and prev.kind == CHARACTER) else CREATURE,
            name or (prev.display_name if prev else None),
            prev.cre_resref if prev and prev.cre_resref else ('' if '#' in key else key),
            ident.script_name, dialog if has_dialog else (prev.dialog if prev else ''),
            bool(sells.get(dialog)) or bool(prev and prev.sells), tuple(seen), ident.general,
            ident.race, ident.klass, ident.gender, ident.alignment, ident.allegiance)
    stamp = now or datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    return Census(build_fingerprint, language, tuple(by_id[k] for k in sorted(by_id)),
                  tuple(sorted(are_data)), stamp)


def write_census(census: Census, base_dir: Path = DEFAULT_CENSUS_DIR, *,
                 repo_root: Path = REPO_ROOT) -> Path:
    """The local catalog (`install-<build>/census.<language>.json`); never inside the repository."""
    target = _install_dir(Path(base_dir), census.build_fingerprint) / f'census.{census.language}.json'
    resolved, repo = target.resolve(), repo_root.resolve()
    if resolved == repo or repo in resolved.parents:
        raise GameDataError('refusing to write game-derived data inside the repository')
    target.parent.mkdir(parents=True, exist_ok=True)
    doc = {'schema': CENSUS_SCHEMA, 'build_fingerprint': census.build_fingerprint,
           'language': census.language, 'generated_at': census.generated_at,
           'source': {'kind': 'GAME_DATA_LOCAL', 'change_request': 'CR-2026-030'},
           'areas': list(census.areas), 'entries': [asdict(e) for e in census.entries]}
    target.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return target


def census_report(census: Census, *, curated: set[str], area_names: dict[str, str]) -> str:
    """A Markdown report for the maintainer (kept outside the repository): how many characters,
    where, which are curated, and a suggested curation queue (dialogue and stores first)."""
    chars = census.characters()
    lines = ['# Censo de personagens (SPEC-012, fase 2, primeiro corte)', '',
             f'- Build `{census.build_fingerprint[:19]}…`, idioma `{census.language}`, '
             f'gerado em {census.generated_at}.',
             f'- Áreas lidas: {len(census.areas)}. Entradas: {len(census.entries)} '
             f'({len(chars)} personagens, {len(census.entries) - len(chars)} criaturas).',
             f'- Personagens com diálogo próprio: {sum(1 for c in chars if c.dialog)}; '
             f'que vendem algo: {sum(1 for c in chars if c.sells)}; '
             f'já com ficha curada: {sum(1 for c in chars if c.entry_id in curated)}.',
             '- O capítulo em que cada um aparece depende dos scripts do jogo e não está nesta '
             'contagem.', '', '## Personagens por área', '',
             '| Área | Nome | Personagens | Com diálogo | Curados |', '|---|---|---|---|---|']
    per_area: dict[str, list[CensusEntry]] = {}
    for c in chars:
        for area in sorted({a.area for a in c.appearances}):
            per_area.setdefault(area, []).append(c)
    for area in sorted(per_area, key=lambda a: (-len(per_area[a]), a)):
        group = per_area[area]
        lines.append(f'| {area} | {area_names.get(area, "")} | {len(group)} | '
                     f'{sum(1 for c in group if c.dialog)} | '
                     f'{sum(1 for c in group if c.entry_id in curated)} |')
    lines += ['', '## Fila sugerida de curadoria', '',
              'Primeiro quem tem diálogo e vende algo, depois quem tem diálogo, nas áreas com '
              'mais gente.', '', '| Ordem | Personagem | Áreas | Diálogo | Vende |',
              '|---|---|---|---|---|']
    queue = sorted((c for c in chars if c.entry_id not in curated and c.dialog),
                   key=lambda c: (not c.sells, -max(len(per_area.get(a.area, ()))
                                                    for a in c.appearances),
                                  c.display_name or '', c.entry_id))
    for i, c in enumerate(queue[:60], 1):
        lines.append(f'| {i} | {c.display_name} (`{c.entry_id}`) | '
                     f'{", ".join(sorted({a.area for a in c.appearances}))} | sim | '
                     f'{"sim" if c.sells else "não"} |')
    return '\n'.join(lines) + '\n'
