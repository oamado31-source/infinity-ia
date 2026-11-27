# SPDX-License-Identifier: Apache-2.0
"""ADR-0150: the game's camera as plain math: projection, footprints, walls with their baseline."""
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.areas.camera import Box, Camera, footprint, occluder  # noqa: E402
from infinity_ai.areas.recipe import Shape  # noqa: E402

CAM = Camera(42.0, 40.0, turn=45.0, u0=640.0, v0=700.0)


class CameraTests(unittest.TestCase):
    def test_ground_and_picture_go_both_ways(self):
        for x, y in ((0, 0), (2.5, -1.2), (-7, 3.3)):
            gx, gy = CAM.ground(*CAM.project(x, y))
            self.assertAlmostEqual(gx, x, places=9)
            self.assertAlmostEqual(gy, y, places=9)

    def test_a_turned_room_has_edges_at_the_sine_of_the_elevation(self):
        u1, v1 = CAM.project(0, 0)
        u2, v2 = CAM.project(1, 0)
        self.assertAlmostEqual(abs(v2 - v1) / abs(u2 - u1), math.sin(math.radians(42)))

    def test_heights_go_up_at_the_cosine(self):
        _u, v0 = CAM.project(0, 0, 0)
        _u, v1 = CAM.project(0, 0, 1)
        self.assertAlmostEqual(v0 - v1, 40 * math.cos(math.radians(42)))


class PartTests(unittest.TestCase):
    def test_the_foot_of_a_part_holds_its_centre(self):
        box = Box(1.0, 2.0, 2.0, 1.0, 1.5, turn=10)
        poly = footprint(CAM, box)
        self.assertEqual(len(poly), 4)
        self.assertTrue(Shape(None, tuple(poly)).contains(*CAM.project(1.0, 2.0)))

    def test_the_wall_starts_with_the_side_corners_of_the_foot(self):
        box = Box(0.0, 0.0, 2.0, 1.0, 1.5)
        wall = occluder(CAM, box)
        feet = [CAM.project(x, y) for x, y in box.foot()]
        left = min(feet, key=lambda p: p[0])
        right = max(feet, key=lambda p: p[0])
        self.assertEqual(wall[0], (round(left[0]), round(left[1])))
        self.assertEqual(wall[1], (round(right[0]), round(right[1])))
        # the rest of the outline is the top: above (smaller v than) the baseline
        self.assertTrue(all(v < max(wall[0][1], wall[1][1]) for _u, v in wall[2:]))
        top = CAM.project(0.0, 0.0, 1.5)
        self.assertTrue(Shape(None, tuple(wall)).contains(*top))

    def test_a_box_square_to_the_picture_gives_a_rectangle_wall(self):
        box = Box(0.0, 0.0, 1.0, 1.0, 2.0, turn=-45)
        wall = occluder(CAM, box)
        self.assertEqual(len(wall), 4)
        self.assertEqual(wall[0][1], wall[1][1])         # a flat baseline
        self.assertLess(wall[2][1], wall[1][1])


if __name__ == '__main__':
    unittest.main()
