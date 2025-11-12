import pytest

from birdie_buddy.round_entry.factories import (
    HoleFactory,
    RoundFactory,
    ShotFactory,
)

from birdie_buddy.users.factories import UserFactory

from birdie_buddy.round_entry.services.putting_stats_service import (
    PuttingStatsService,
)


@pytest.mark.django_db
class TestPuttingStatsService:
    def test_make_rate_0_3_no_putts(self):
        user = UserFactory()
        service = PuttingStatsService()
        assert service.make_rate_0_3(user) == 0.0

    def test_make_rate_0_3_all_made(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=1)

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole2, number=3, lie="green", start_distance=2)

        assert service.make_rate_0_3(user) == 100.0

    def test_make_rate_0_3_none_made(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=3)
        ShotFactory(user=user, hole=hole1, number=4, lie="green", start_distance=4)

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole2, number=3, lie="green", start_distance=2)
        ShotFactory(user=user, hole=hole2, number=4, lie="green", start_distance=4)

        assert service.make_rate_0_3(user) == 0

    def test_make_rate_0_3_some_made(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=2)

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole2, number=3, lie="green", start_distance=2)
        ShotFactory(user=user, hole=hole2, number=4, lie="green", start_distance=1)

        assert service.make_rate_0_3(user) == pytest.approx(2 / 3 * 100)

    def test_make_rate_3_6(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=4)

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole2, number=3, lie="green", start_distance=5)
        ShotFactory(user=user, hole=hole2, number=4, lie="green", start_distance=1)

        assert service.make_rate_3_6(user) == 50.0

    def test_make_rate_6_9(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=7.5)

        assert service.make_rate_6_9(user) == 100.0

    def test_make_rate_9_12(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=10.5)

        assert service.make_rate_9_12(user) == 100.0

    def test_make_rate_12_15(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=13.5)

        assert service.make_rate_12_15(user) == 100.0

    def test_make_rate_15_20(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=16.5)

        assert service.make_rate_15_20(user) == 100.0

    def test_make_rate_20_30(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=24.0)

        assert service.make_rate_20_30(user) == 100.0

    def test_make_rate_30_40(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=33.0)

        assert service.make_rate_30_40(user) == 100.0

    def test_make_rate_40_plus(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=45.0)

        assert service.make_rate_40_plus(user) == 100.0

    def test_make_rate_excludes_other_distance_ranges(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=2)

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole2, number=3, lie="green", start_distance=15.0)

        assert service.make_rate_0_3(user) == 100.0
        assert service.make_rate_15_20(user) == 100.0
        assert service.make_rate_3_6(user) == 0.0

    def test_get_for_user(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=1.5)

        stats = service.get_for_user(user)

        assert hasattr(stats, "make_rate_0_3")
        assert hasattr(stats, "make_rate_3_6")
        assert hasattr(stats, "make_rate_6_9")
        assert hasattr(stats, "make_rate_9_12")
        assert hasattr(stats, "make_rate_12_15")
        assert hasattr(stats, "make_rate_15_20")
        assert hasattr(stats, "make_rate_20_30")
        assert hasattr(stats, "make_rate_30_40")
        assert hasattr(stats, "make_rate_40_plus")
        assert hasattr(stats, "strokes_gained_0_3_per_18")
        assert hasattr(stats, "strokes_gained_3_6_per_18")
        assert hasattr(stats, "strokes_gained_6_9_per_18")
        assert hasattr(stats, "strokes_gained_9_12_per_18")
        assert hasattr(stats, "strokes_gained_12_15_per_18")
        assert hasattr(stats, "strokes_gained_15_20_per_18")
        assert hasattr(stats, "strokes_gained_20_30_per_18")
        assert hasattr(stats, "strokes_gained_30_40_per_18")
        assert hasattr(stats, "strokes_gained_40_plus_per_18")
        assert stats.make_rate_0_3 == 100.0

    def test_strokes_gained_0_3_no_putts(self):
        user = UserFactory()
        service = PuttingStatsService()
        assert service.strokes_gained_0_3(user) == 0.0

    def test_strokes_gained_0_3_with_putts(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=2,
            strokes_gained=0.3,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.0,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.0,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="green",
            start_distance=1,
            strokes_gained=-0.1,
        )

        expected = (0.3 + (-0.1)) / 2 * 18
        assert service.strokes_gained_0_3(user) == pytest.approx(expected)

    def test_strokes_gained_3_6(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=4,
            strokes_gained=0.15,
        )

        expected = 0.15 / 1 * 18
        assert service.strokes_gained_3_6(user) == pytest.approx(expected)

    def test_strokes_gained_6_9(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=7.5,
            strokes_gained=-0.25,
        )

        expected = -0.25 / 1 * 18
        assert service.strokes_gained_6_9(user) == pytest.approx(expected)

    def test_strokes_gained_9_12(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10.5,
            strokes_gained=0.4,
        )

        expected = 0.4 / 1 * 18
        assert service.strokes_gained_9_12(user) == pytest.approx(expected)

    def test_strokes_gained_12_15(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=13.5,
            strokes_gained=-0.5,
        )

        expected = -0.5 / 1 * 18
        assert service.strokes_gained_12_15(user) == pytest.approx(expected)

    def test_strokes_gained_15_20(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=16.5,
            strokes_gained=0.3,
        )

        expected = 0.3 / 1 * 18
        assert service.strokes_gained_15_20(user) == pytest.approx(expected)

    def test_strokes_gained_20_30(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=24.0,
            strokes_gained=0.1,
        )

        expected = 0.1 / 1 * 18
        assert service.strokes_gained_20_30(user) == pytest.approx(expected)

    def test_strokes_gained_30_40(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=33.0,
            strokes_gained=-0.2,
        )

        expected = -0.2 / 1 * 18
        assert service.strokes_gained_30_40(user) == pytest.approx(expected)

    def test_strokes_gained_40_plus(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=45.0,
            strokes_gained=0.5,
        )

        expected = 0.5 / 1 * 18
        assert service.strokes_gained_40_plus(user) == pytest.approx(expected)

    def test_strokes_gained_excludes_other_distance_ranges(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=2,
            strokes_gained=0.5,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="green",
            start_distance=16.5,
            strokes_gained=-0.3,
        )

        expected_0_3 = 0.5 / 2 * 18
        expected_15_20 = -0.3 / 2 * 18
        assert service.strokes_gained_0_3(user) == pytest.approx(expected_0_3)
        assert service.strokes_gained_15_20(user) == pytest.approx(expected_15_20)
        assert service.strokes_gained_3_6(user) == 0.0

    def test_strokes_gained_multiple_holes_normalization(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=0.6,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="green",
            start_distance=11,
            strokes_gained=-0.4,
        )

        expected = (0.6 + (-0.4)) / 2 * 18
        assert service.strokes_gained_9_12(user) == pytest.approx(expected)

    def test_strokes_gained_holes_without_putts_in_range_included_in_normalization(
        self,
    ):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=0.9,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="green",
            start_distance=2,
            strokes_gained=0.3,
        )

        expected = 0.9 / 2 * 18
        assert service.strokes_gained_9_12(user) == pytest.approx(expected)

    def test_get_for_round(self):
        user = UserFactory()
        service = PuttingStatsService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=2,
            strokes_gained=0.5,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=150,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=-0.3,
        )

        stats = service.get_for_round(round)

        assert hasattr(stats, "strokes_gained_0_3")
        assert hasattr(stats, "strokes_gained_9_12")
        assert stats.strokes_gained_0_3 == pytest.approx(0.5)
        assert stats.strokes_gained_9_12 == pytest.approx(-0.3)

