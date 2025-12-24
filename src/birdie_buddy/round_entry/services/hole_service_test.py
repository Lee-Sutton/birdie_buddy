import pytest
from birdie_buddy.round_entry.factories.hole_factory import HoleFactory
from birdie_buddy.round_entry.factories.shot_factory import ShotFactory
from birdie_buddy.round_entry.models import Hole
from birdie_buddy.round_entry.services.hole_service import HoleService


@pytest.fixture
def round(user):
    from birdie_buddy.round_entry.factories.round_factory import RoundFactory
    return RoundFactory(user=user, course_name="Test Course", holes_played=6)


class TestHoleService:
    """Tests for HoleService business logic."""

    def test_delete_middle_hole_renumbers_subsequent_holes(self, round, user):
        """Test that deleting a middle hole renumbers all subsequent holes."""
        # Create holes 1-6
        holes = [
            HoleFactory(user=user, round=round, number=i, par=4, score=4, mental_scorecard=4)
            for i in range(1, 7)
        ]

        # Delete hole 3
        HoleService.delete_hole(holes[2])

        # Verify hole 3 is deleted
        assert not Hole.objects.filter(pk=holes[2].pk).exists()

        # Verify remaining holes are renumbered: 1, 2, 3, 4, 5 (was 1, 2, 4, 5, 6)
        remaining_holes = Hole.objects.filter(round=round).order_by('number')
        assert remaining_holes.count() == 5

        hole_numbers = [h.number for h in remaining_holes]
        assert hole_numbers == [1, 2, 3, 4, 5]  # Sequential, no gaps

        # Verify holes_played is decremented
        round.refresh_from_db()
        assert round.holes_played == 5

    def test_delete_first_hole_renumbers_all_holes(self, round, user):
        """Test that deleting the first hole renumbers all remaining holes."""
        holes = [
            HoleFactory(user=user, round=round, number=i, par=4, score=5, mental_scorecard=5)
            for i in range(1, 5)
        ]
        round.holes_played = 4
        round.save()

        # Delete hole 1
        HoleService.delete_hole(holes[0])

        # Verify renumbering: was [1, 2, 3, 4], now [1, 2, 3]
        remaining_holes = Hole.objects.filter(round=round).order_by('number')
        assert remaining_holes.count() == 3
        assert [h.number for h in remaining_holes] == [1, 2, 3]

        round.refresh_from_db()
        assert round.holes_played == 3

    def test_delete_last_hole_no_renumbering_needed(self, round, user):
        """Test that deleting the last hole doesn't require renumbering."""
        holes = [
            HoleFactory(user=user, round=round, number=i, par=4, score=4, mental_scorecard=4)
            for i in range(1, 4)
        ]
        round.holes_played = 3
        round.save()

        # Delete hole 3 (last hole)
        HoleService.delete_hole(holes[2])

        # Verify holes 1 and 2 remain unchanged
        remaining_holes = Hole.objects.filter(round=round).order_by('number')
        assert remaining_holes.count() == 2
        assert [h.number for h in remaining_holes] == [1, 2]

        round.refresh_from_db()
        assert round.holes_played == 2

    def test_round_complete_property_after_deletion(self, round, user):
        """Test that round.complete remains accurate after hole deletion."""
        # Create complete round: 3 holes with shots
        holes = []
        for i in range(1, 4):
            hole = HoleFactory(user=user, round=round, number=i, par=4, score=4, mental_scorecard=4)
            ShotFactory(hole=hole, user=user, start_distance=100, lie="fairway")
            holes.append(hole)

        round.holes_played = 3
        round.save()

        # Verify round is complete
        assert round.complete is True

        # Delete hole 2
        HoleService.delete_hole(holes[1])

        # Verify round is still complete (2 holes with shots, holes_played=2)
        round.refresh_from_db()
        assert round.holes_played == 2
        assert round.complete is True  # Should remain complete
