from birdie_buddy.round_entry.factories.hole_factory import (
    HoleFactory,
)
from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.round_entry.factories.shot_factory import ShotFactory
from birdie_buddy.round_entry.models import Hole
from django.core.exceptions import ValidationError
import pytest


class TestStrokesGained:
    def test_strokes_gained(self, db, user):
        """
        The hole strokes gained is calculated as the difference between
        the scoring average for the hole length minus the score
        """

        hole = HoleFactory.par_3_par()
        assert hole.strokes_gained == pytest.approx(0.085)


class TestRound:
    def test_complete_true_when_all_holes_have_shots(self, db, user):
        round = RoundFactory(user=user, holes_played=2)
        hole1 = HoleFactory(round=round, user=user, number=1)
        hole2 = HoleFactory(round=round, user=user, number=2)
        ShotFactory(hole=hole1, user=user)
        ShotFactory(hole=hole2, user=user)

        assert round.complete is True

    def test_complete_is_false_if_hole_is_missing_shots(self, db, user):
        round = RoundFactory(user=user, holes_played=2)
        hole1 = HoleFactory(round=round, user=user, number=1)
        hole2 = HoleFactory(round=round, user=user, number=2)
        ShotFactory(hole=hole1, user=user)

        assert round.complete is False

    def test_complete_false_if_not_enough_holes(self, db, user):
        round = RoundFactory(user=user, holes_played=2)
        hole1 = HoleFactory(round=round, user=user, number=1)
        ShotFactory(hole=hole1, user=user)

        assert round.complete is False


class TestStrokesGainedDriving:
    def test_driver_gained(self, db):
        hole: Hole = HoleFactory.par_4_par()
        expected_sg = 3.99 - 2.88 - 1  # 3.99 from 400 yds tee - 2.88 from 130 in FW
        assert hole.strokes_gained_driving == pytest.approx(expected_sg)

    def test_returns_0_if_tee_shot_is_approach(self, db):
        """The tee shot is considered an approach shot if the hole is less than a par 4"""
        hole: Hole = HoleFactory.par_3_par()
        assert hole.strokes_gained_driving == 0

    def test_hole_in_one(self, db):
        hole: Hole = HoleFactory.par_4_hole_in_one()
        assert hole.strokes_gained_driving == pytest.approx(2.714)


class TestStrokesGainedApproach:
    def test_sg_approach(self, db):
        hole: Hole = HoleFactory.par_4_par()

        expected_sg = 2.88 - 1.78 - 1  # 130 yds from fairway to 15 feet on green
        assert hole.strokes_gained_approach == expected_sg

    def test_sg_approach_multiple_approach_shots(self, db):
        hole: Hole = HoleFactory.par_5_par()

        expected_sg = (3.595 - 2.98 - 1) + (2.98 - 1.78 - 1)
        assert hole.strokes_gained_approach == expected_sg

    def test_sg_approach_holeout(self, db):
        hole: Hole = HoleFactory.par_4_eagle()

        assert hole.strokes_gained_approach == 1.75

    def test_sg_par_3(self, db):
        hole: Hole = HoleFactory.par_3_par()
        assert hole.strokes_gained_driving == 0
        assert hole.strokes_gained_approach == pytest.approx(0.215)


class TestStrokesGainedPutting:
    def test_sg_putting(self, db):
        hole: Hole = HoleFactory.par_4_par()

        expected_sg = 1.78 - 1.04 - 1 + 1.04 - 1
        assert hole.strokes_gained_putting == expected_sg


class TestShotDistanceConversion:
    def test_yards_converted_to_feet(self, db, user):
        hole = HoleFactory(user=user)
        shot = ShotFactory(hole=hole, user=user, start_distance=100, lie="fairway")
        assert shot.yards == 100
        assert shot.feet == 300

    def test_feet_converted_to_yards_for_putts(self, db, user):
        hole = HoleFactory(user=user)
        shot = ShotFactory(hole=hole, user=user, start_distance=15, lie="green")
        assert shot.feet == 15
        assert shot.yards == 5

    def test_feet_to_yards_conversion(self, db, user):
        hole = HoleFactory(user=user)
        shot = ShotFactory(hole=hole, user=user, start_distance=30, lie="green")
        assert shot._feet_to_yards(30) == 10

    def test_yards_to_feet_conversion(self, db, user):
        hole = HoleFactory(user=user)
        shot = ShotFactory(hole=hole, user=user, start_distance=10, lie="fairway")
        assert shot._yards_to_feet(10) == 30


class TestShotTypeAutoDetection:
    def test_putt_shot_type(self, db, user):
        hole = HoleFactory(user=user)
        shot = ShotFactory(hole=hole, user=user, start_distance=10, lie="green")
        assert shot.shot_type == "putt"

    def test_drive_shot_type(self, db, user):
        hole = HoleFactory(user=user, par=4)
        shot = ShotFactory(hole=hole, user=user, start_distance=300, lie="tee")
        assert shot.shot_type == "drive"

    def test_approach_shot_type(self, db, user):
        hole = HoleFactory(user=user)
        shot = ShotFactory(hole=hole, user=user, start_distance=150, lie="fairway")
        assert shot.shot_type == "approach"

    def test_around_green_shot_type(self, db, user):
        hole = HoleFactory(user=user)
        shot = ShotFactory(hole=hole, user=user, start_distance=20, lie="rough")
        assert shot.shot_type == "around_green"


class TestMentalScorecardValidation:
    def test_mental_scorecard_cannot_exceed_score(self, db, user):
        hole = HoleFactory(user=user, score=5, mental_scorecard=6, number=1)
        with pytest.raises(ValidationError) as exc_info:
            hole.full_clean()
        assert "mental_scorecard" in exc_info.value.message_dict

    def test_mental_scorecard_equal_to_score_is_valid(self, db, user):
        hole = HoleFactory(user=user, score=5, mental_scorecard=5, number=1)
        hole.full_clean()

    def test_mental_scorecard_less_than_score_is_valid(self, db, user):
        hole = HoleFactory(user=user, score=5, mental_scorecard=4, number=1)
        hole.full_clean()

    def test_mental_scorecard_none_is_valid(self, db, user):
        hole = HoleFactory(user=user, score=5, number=1)
        hole.full_clean()
