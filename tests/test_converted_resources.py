# SPDX-License-Identifier: Apache-2.0
"""SPEC-012 / CR-2026-032: the local inventory of resources converted from other games."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.encyclopedia.resources import (  # noqa: E402
    RESOURCE_SCHEMA, load_inventory, load_schema, load_sources, problems, save_entry,
)

try:
    import jsonschema  # type: ignore
except ImportError:  # pragma: no cover
    jsonschema = None


def schema_check(doc, schema):
    validator = jsonschema.Draft202012Validator(schema)
    return [e.message for e in validator.iter_errors(doc)]


BUILD = 'sha256:' + 'ab' * 32
ENTRY = {
    'schema': RESOURCE_SCHEMA, 'resource_id': 'converted:teste-gigante',
    'source_game': 'IWD', 'source_creature_id': 'TESTE01', 'converted_cre_id': 'IATESTE',
    'script_name': 'INFAI_TESTE', 'animation_ref': '0xE251 GIANT_VERBEEG',
    'animation_assets': [{'resref': 'E251', 'type': 'INI', 'present': True, 'from': 'build'},
                         {'resref': 'MGVEA1', 'type': 'BAM', 'present': True,
                          'from': 'projeto-teste: 3dca1.bam'}],
    'sound_refs': [{'resref': 'VERBEE01', 'type': 'WAV', 'present': True}],
    'original_stats_ref': 'sheets/adnd/teste.json', 'converted_stats_ref': 'templates.json#IATESTE',
    'conversion_source': 'infinity-animations', 'target_engine': 'BG2EE',
    'rights_status': {'license': 'NONE', 'use': 'LAB_ONLY', 'approved_by': 'mantenedor',
                      'approved_at': '2026-11-23'},
    'validation_status': 'DRAWN_IN_GAME', 'evidence_ref': 'docs/evidence/S2c.md',
    'recorded_at': '2026-11-23',
}


class SourcesTests(unittest.TestCase):
    def test_conversion_projects_are_registered_with_their_license(self):
        sources = load_sources()
        kinds = {sid: s['kind'] for sid, s in sources.items()}
        for sid in ('infinity-animations', 'totlm-bg2ee', 'iwd1-eet', 'iwd2-eet', 'nwnforbg',
                    'iwdification'):
            self.assertEqual(kinds[sid], 'CONVERSION_PROJECT', sid)
            self.assertIn('license', sources[sid])
        self.assertEqual(kinds['portraitscout'], 'TOOL')
        self.assertEqual(sources['totlm-bg2ee']['license'], 'CC-BY-SA-4.0')
        self.assertEqual(sources['infinity-animations']['license'], 'NONE')


@unittest.skipIf(jsonschema is None, 'jsonschema not installed')
class InventoryTests(unittest.TestCase):
    def check(self, entries):
        return problems(entries, sources=load_sources(), schema=load_schema(),
                        schema_check=schema_check)

    def test_a_good_entry_passes_and_the_schema_is_strict(self):
        self.assertEqual(self.check([ENTRY]), [])
        for change in (lambda e: e.update(converted_cre_id='MTOWN6'),       # not one of ours
                       lambda e: e.update(validation_status='OK'),
                       lambda e: e.update(hp=28),                            # no game numbers
                       lambda e: e['animation_assets'][0].update(type='PNG'),
                       lambda e: e.update(animation_ref='GIANT_VERBEEG')):
            doc = copy.deepcopy(ENTRY)
            change(doc)
            self.assertTrue(self.check([doc]), doc)

    def test_rights_states_and_uniqueness(self):
        def with_(**kw):
            doc = copy.deepcopy(ENTRY)
            for k, v in kw.items():
                doc[k] = v
            return doc
        open_use = with_(rights_status={'license': 'NONE', 'use': 'OPEN'})
        self.assertTrue(any('OPEN' in p for p in self.check([open_use])))
        no_ok = with_(rights_status={'license': 'NONE', 'use': 'LAB_ONLY'})
        self.assertTrue(any('aceite' in p for p in self.check([no_ok])))
        cc = with_(conversion_source='totlm-bg2ee',
                   rights_status={'license': 'CC-BY-SA-4.0', 'use': 'OPEN'})
        self.assertEqual(self.check([cc]), [])
        missing = copy.deepcopy(ENTRY)
        missing['animation_assets'][1]['present'] = False
        self.assertTrue(any('ausentes' in p for p in self.check([missing])))
        missing['validation_status'] = 'DECLARED'
        self.assertEqual(self.check([missing]), [])                 # declared may lack files
        no_proof = copy.deepcopy(ENTRY)
        del no_proof['evidence_ref']
        self.assertTrue(any('sem evidência' in p for p in self.check([no_proof])))
        twin = with_(resource_id='converted:outro')
        self.assertTrue(any('converted_cre_id repetido' in p for p in self.check([ENTRY, twin])))
        self.assertTrue(any('fonte desconhecida' in p
                            for p in self.check([with_(conversion_source='site-inventado')])))

    def test_the_inventory_is_local_and_per_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = save_entry(BUILD, ENTRY, Path(tmp))
            self.assertTrue(str(path).startswith(tmp))
            self.assertEqual([e['resource_id'] for e in load_inventory(BUILD, Path(tmp))],
                             ['converted:teste-gigante'])
            save_entry(BUILD, dict(ENTRY, validation_status='APPROVED'), Path(tmp))
            self.assertEqual(len(load_inventory(BUILD, Path(tmp))), 1)       # replaced
            self.assertEqual(load_inventory('sha256:' + 'cd' * 32, Path(tmp)), [])
            doc = json.loads(path.read_text())
            self.assertEqual(doc['build_fingerprint'], BUILD)


if __name__ == '__main__':
    unittest.main()
