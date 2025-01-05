from birdie_buddy.round_entry.factories.hole_factory import HoleFactory
from birdie_buddy.round_entry.models import Hole
import pytest


class TestHole:
    def test_strokes_gained(self, db):
        """
        The hole strokes gained is calculated as the difference between
        the scoring average for the hole length minus the score
        """
        hole: Hole = HoleFactory.par_5_birdie()
        assert hole.strokes_gained == pytest.approx(0.41)
