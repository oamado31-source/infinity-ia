# SPDX-License-Identifier: Apache-2.0
"""CR-2026-029: lands people only talk about are never a generated person's origin or trip."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.canon.pack import KNOWLEDGE_ROOT, CanonError, load_partition  # noqa: E402
from infinity_ai.personality.identity import generate_identity  # noqa: E402

PACK = load_partition(1369)


class TalkOnlyTests(unittest.TestCase):
    def test_the_listed_regions_and_everything_below_them(self):
        self.assertEqual(PACK.talk_only,
                         {'region:kara-tur', 'region:underdark', 'region:menzoberranzan'})

    def test_no_generated_background_comes_from_or_went_to_them(self):
        for i in range(400):
            for home in ('region:athkatla', 'region:baldurs-gate'):
                doc = generate_identity(npc_id=f'npc:cre-eval{i}', role='PATRON', gender=1,
                                        home_region=home, pack=PACK, world_seed='w',
                                        campaign_id='c', branch_id='b')
                touched = {doc['origin_region'], *doc['places_visited']}
                self.assertFalse(touched & PACK.talk_only, (i, home, doc))

    def test_the_list_is_part_of_the_revision_and_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'knowledge'
            shutil.copytree(KNOWLEDGE_ROOT, root)
            manifest = root / 'periods' / '1369-DR' / 'manifest.json'
            doc = json.loads(manifest.read_text(encoding='utf-8'))
            doc['talk_only_regions'] = ['region:kara-tur']
            manifest.write_text(json.dumps(doc), encoding='utf-8')
            self.assertNotEqual(load_partition(1369, root).revision, PACK.revision)
            doc['talk_only_regions'] = ['char:lolth']
            manifest.write_text(json.dumps(doc), encoding='utf-8')
            with self.assertRaises(CanonError):
                load_partition(1369, root)


if __name__ == '__main__':
    unittest.main()
