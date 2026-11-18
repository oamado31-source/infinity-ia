# SPDX-License-Identifier: Apache-2.0
"""SPEC-012 / CR-2026-030: the curated encyclopedia records kept in the repository.

Records live in `knowledge/encyclopedia/<category dir>/**.json`, one per entity, each validated by
its versioned schema. This module loads them and reports every problem it finds:
- the schema (strict: extracted game attributes are not fields of any schema);
- a stable, unique `canonical_id` whose prefix matches the category and the directory;
- relationships that point to an existing record, or are marked `pending:`;
- sources that exist (`sources.json` or `knowledge/sources/`);
- curation refs that point to an existing curation file with the same NPC.
A record never grants knowledge to a NPC (SPEC-012 §10.1): it is a catalog, not memory.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASE = ROOT / 'knowledge' / 'encyclopedia'
PREFIX = {'CHARACTER': 'character', 'CREATURE': 'creature', 'ITEM': 'item', 'SPELL': 'spell',
          'RACE': 'race', 'CLASS': 'class', 'FACTION': 'faction', 'QUEST': 'quest',
          'EVENT': 'event', 'LOCATION': 'location'}


@dataclass(frozen=True)
class Record:
    path: Path
    doc: dict

    @property
    def canonical_id(self) -> str:
        return self.doc.get('canonical_id', '')


def load_manifest(base: Path = DEFAULT_BASE) -> dict:
    return json.loads((Path(base) / 'manifest.json').read_text(encoding='utf-8'))


def load_records(base: Path = DEFAULT_BASE) -> list[Record]:
    manifest = load_manifest(base)
    out = []
    for cat in manifest['categories']:
        folder = Path(base) / cat['dir']
        if folder.is_dir():
            out += [Record(p, json.loads(p.read_text(encoding='utf-8')))
                    for p in sorted(folder.rglob('*.json'))]
    return out


def source_ids(base: Path = DEFAULT_BASE) -> set[str]:
    doc = json.loads((Path(base) / 'sources.json').read_text(encoding='utf-8'))
    ids = {s['source_id'] for s in doc['sources']}
    books = Path(base).parent / 'sources'
    if books.is_dir():
        ids |= {json.loads(p.read_text(encoding='utf-8')).get('source_id')
                for p in books.glob('*.json')}
    return ids


def problems(base: Path = DEFAULT_BASE, *, schema_check=None) -> list[str]:
    """Every problem of the encyclopedia. `schema_check(record_doc, schema_doc) -> list[str]`
    validates one record against its schema (the tests pass a jsonschema validator)."""
    base = Path(base)
    manifest = load_manifest(base)
    by_cat = {c['category']: c for c in manifest['categories']}
    records = load_records(base)
    ids: dict[str, Path] = {}
    out: list[str] = []
    known_sources = source_ids(base)
    for rec in records:
        where = rec.path.relative_to(base)
        cat = rec.doc.get('category')
        info = by_cat.get(cat)
        if info is None:
            out.append(f'{where}: categoria desconhecida {cat!r}')
            continue
        if where.parts[0] != info['dir']:
            out.append(f'{where}: categoria {cat} fora de {info["dir"]}/')
        if schema_check is not None:
            schema = json.loads((base / info['schema']).read_text(encoding='utf-8'))
            out += [f'{where}: {msg}' for msg in schema_check(rec.doc, schema)]
        cid = rec.canonical_id
        if not cid.startswith(PREFIX[cat] + ':'):
            out.append(f'{where}: canonical_id {cid!r} não começa com {PREFIX[cat]}:')
        if cid in ids:
            out.append(f'{where}: canonical_id repetido (também em {ids[cid].relative_to(base)})')
        ids[cid] = rec.path
        for s in rec.doc.get('source_refs') or ():
            if s not in known_sources:
                out.append(f'{where}: fonte desconhecida {s!r}')
        curation = (rec.doc.get('refs') or {}).get('curation')
        if curation:
            path = ROOT / curation if base == DEFAULT_BASE else base.parent.parent / curation
            if not path.is_file():
                out.append(f'{where}: ficha {curation} não existe')
    for rec in records:
        for rel in rec.doc.get('relationships') or ():
            target = rel.get('target', '')
            if not target.startswith('pending:') and target not in ids:
                out.append(f'{rec.path.relative_to(base)}: relação para {target!r}, que não '
                           'existe (marque pending: se for de propósito)')
    return out
