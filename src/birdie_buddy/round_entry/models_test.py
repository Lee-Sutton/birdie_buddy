from birdie_buddy.round_entry.factories.hole_factory import (
    HoleFactory,
)
from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.round_entry.factories.shot_factory import ShotFactory
from birdie_buddy.round_entry.models import Hole
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
    @pytest.mark.parametrize(
        "attr",
        [
            "strokes_gained_driving",
            "strokes_gained_approach",
            "strokes_gained_putting",
            "strokes_gained_around_the_green",
        ],
    )
    def test_round_strokes_gained(self, attr, db):
        round = RoundFactory()

        hole: Hole = HoleFactory.par_4_par()
        hole.round = round
        hole.save()

        hole2 = HoleFactory.par_5_par()
        hole2.round = round
        hole2.save()

        assert getattr(round, attr) == getattr(hole, attr) + getattr(hole2, attr)

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
