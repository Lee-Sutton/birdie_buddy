import pytest

from birdie_buddy.round_entry.factories import (
    HoleFactory,
    RoundFactory,
    ShotFactory,
)

from birdie_buddy.users.factories import UserFactory

from birdie_buddy.round_entry.services.short_game_service import (
    ShortGameService,
)


@pytest.mark.django_db
class TestShortGameService:
    def test_two_chip_percentage_calculation(self):
        user = UserFactory()
        service = ShortGameService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            shot_type="tee",
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            shot_type="around_green",
            lie="fairway",
            start_distance=8,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            shot_type="around_green",
            lie="fairway",
            start_distance=5,
            strokes_gained=0.0,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=4,
            shot_type="putt",
            lie="green",
            start_distance=3,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            shot_type="tee",
            lie="tee",
            start_distance=380,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            shot_type="around_green",
            lie="fairway",
            start_distance=9,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            shot_type="putt",
            lie="green",
            start_distance=4,
            strokes_gained=0.0,
        )

        hole3 = HoleFactory(user=user, round=round, par=4, number=3)
        ShotFactory(
            user=user,
            hole=hole3,
            number=1,
            shot_type="tee",
            lie="tee",
            start_distance=390,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=2,
            shot_type="around_green",
            lie="rough",
            start_distance=15,
            strokes_gained=-0.1,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=3,
            shot_type="around_green",
            lie="rough",
            start_distance=12,
            strokes_gained=-0.2,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=4,
            shot_type="putt",
            lie="green",
            start_distance=4,
            strokes_gained=0.0,
        )

        stats = service.get_for_user(user)

        assert stats.two_chip_pct_0_10_fairway == pytest.approx(50.0)
        assert stats.two_chip_pct_10_20_rough == pytest.approx(100.0)

    def test_get_for_user_returns_all_proximity_stats(self):
        user = UserFactory()
        service = ShortGameService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            shot_type="tee",
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            shot_type="approach",
            lie="fairway",
            start_distance=120,
            strokes_gained=0.4,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            shot_type="around_green",
            lie="fairway",
            start_distance=8,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=4,
            shot_type="putt",
            lie="green",
            start_distance=5,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            shot_type="tee",
            lie="tee",
            start_distance=380,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            shot_type="approach",
            lie="rough",
            start_distance=90,
            strokes_gained=-0.3,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            shot_type="around_green",
            lie="rough",
            start_distance=15,
            strokes_gained=-0.2,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            shot_type="putt",
            lie="green",
            start_distance=8,
            strokes_gained=0.2,
        )

        hole3 = HoleFactory(user=user, round=round, par=5, number=3)
        ShotFactory(
            user=user,
            hole=hole3,
            number=1,
            shot_type="tee",
            lie="tee",
            start_distance=550,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=2,
            shot_type="approach",
            lie="fairway",
            start_distance=280,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=3,
            shot_type="approach",
            lie="fairway",
            start_distance=50,
            strokes_gained=0.5,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=4,
            shot_type="around_green",
            lie="sand",
            start_distance=25,
            strokes_gained=-0.1,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=5,
            shot_type="putt",
            lie="green",
            start_distance=6,
            strokes_gained=0.0,
        )

        stats = service.get_for_user(user)

        assert hasattr(stats, "avg_proximity_0_10_fairway")
        assert hasattr(stats, "avg_proximity_0_10_rough")
        assert hasattr(stats, "avg_proximity_10_20_fairway")
        assert hasattr(stats, "avg_proximity_10_20_rough")
        assert hasattr(stats, "avg_proximity_20_30_fairway")
        assert hasattr(stats, "avg_proximity_20_30_rough")
        assert hasattr(stats, "avg_proximity_sand")

        assert stats.avg_proximity_0_10_fairway == pytest.approx(5.0)
        assert stats.avg_proximity_0_10_rough == 0.0
        assert stats.avg_proximity_10_20_fairway == 0.0
        assert stats.avg_proximity_10_20_rough == pytest.approx(8.0)
        assert stats.avg_proximity_20_30_fairway == 0.0
        assert stats.avg_proximity_20_30_rough == 0.0
        assert stats.avg_proximity_sand == pytest.approx(6.0)

        assert hasattr(stats, "two_chip_pct_0_10_fairway")
        assert hasattr(stats, "two_chip_pct_0_10_rough")
        assert hasattr(stats, "two_chip_pct_10_20_fairway")
        assert hasattr(stats, "two_chip_pct_10_20_rough")
        assert hasattr(stats, "two_chip_pct_20_30_fairway")
        assert hasattr(stats, "two_chip_pct_20_30_rough")
        assert hasattr(stats, "two_chip_pct_sand")

        assert stats.two_chip_pct_0_10_fairway == 0.0
        assert stats.two_chip_pct_0_10_rough == 0.0
        assert stats.two_chip_pct_10_20_fairway == 0.0
        assert stats.two_chip_pct_10_20_rough == 0.0
        assert stats.two_chip_pct_20_30_fairway == 0.0
        assert stats.two_chip_pct_20_30_rough == 0.0
        assert stats.two_chip_pct_sand == 0.0

        assert hasattr(stats, "strokes_gained_0_10_fairway_per_18")
        assert hasattr(stats, "strokes_gained_0_10_rough_per_18")
        assert hasattr(stats, "strokes_gained_10_20_fairway_per_18")
        assert hasattr(stats, "strokes_gained_10_20_rough_per_18")
        assert hasattr(stats, "strokes_gained_20_30_fairway_per_18")
        assert hasattr(stats, "strokes_gained_20_30_rough_per_18")
        assert hasattr(stats, "strokes_gained_sand_per_18")

        assert stats.strokes_gained_0_10_fairway_per_18 == pytest.approx(0.6)
        assert stats.strokes_gained_0_10_rough_per_18 == 0.0
        assert stats.strokes_gained_10_20_fairway_per_18 == 0.0
        assert stats.strokes_gained_10_20_rough_per_18 == pytest.approx(-1.2)
        assert stats.strokes_gained_20_30_fairway_per_18 == 0.0
        assert stats.strokes_gained_20_30_rough_per_18 == 0.0
        assert stats.strokes_gained_sand_per_18 == pytest.approx(-0.6)
