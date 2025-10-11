"""
Tests for the driving stats service.
"""

import pytest

from birdie_buddy.round_entry.factories import (
    HoleFactory,
    RoundFactory,
    ShotFactory,
)

from birdie_buddy.users.factories import UserFactory

from birdie_buddy.round_entry.services.driving_stats import (
    DrivingStats,
    DrivingStatsService,
)

# pytestmark = pytest.mark.skip


@pytest.mark.django_db
class TestDrivingStatsService:
    def test_penalties_per_18_no_holes(self):
        user = UserFactory()
        service = DrivingStatsService()
        assert service.penalties_per_18(user) == 0.0

    def test_penalties_per_18_no_penalties(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with normal sequence
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=10)

        # Par 5 hole with normal sequence
        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=250)
        ShotFactory(user=user, hole=hole2, number=3, lie="rough", start_distance=100)

        assert service.penalties_per_18(user) == 0.0

    def test_penalties_per_18_with_penalties(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with penalty second shot
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="penalty", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=3, lie="rough", start_distance=200)

        # Par 5 hole with penalty second shot
        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="penalty", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=3, lie="fairway", start_distance=300)

        # Par 4 hole with normal sequence (no penalty)
        hole3 = HoleFactory(user=user, round=round, par=4, number=3)
        ShotFactory(user=user, hole=hole3, number=1, lie="tee", start_distance=380)
        ShotFactory(user=user, hole=hole3, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole3, number=3, lie="green", start_distance=10)

        # Par 3 hole with penalty (should be ignored)
        hole4 = HoleFactory(user=user, round=round, par=3, number=4)
        ShotFactory(user=user, hole=hole4, number=1, lie="tee", start_distance=180)
        ShotFactory(user=user, hole=hole4, number=2, lie="penalty", start_distance=180)

        # 2 penalty holes out of 3 par 4/5 holes
        # Expected: (2/3) * 18 = 12.0
        expected_penalties = (2 / 3) * DrivingStatsService.DRIVES_PER_18
        assert service.penalties_per_18(user) == pytest.approx(expected_penalties)

    def test_penalties_per_18_partial_round(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Only 2 holes played, 1 with penalty
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="penalty", start_distance=400)

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=250)

        # 1 penalty hole out of 2 par 4/5 holes
        # Expected: (1/2) * 18 = 9.0
        expected_penalties = (1 / 2) * DrivingStatsService.DRIVES_PER_18
        assert service.penalties_per_18(user) == pytest.approx(expected_penalties)

    def test_get_for_user_includes_penalties(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with penalty second shot
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="penalty", start_distance=400)

        stats = service.get_for_user(user)

        # Should have penalties_per_18 field populated
        assert hasattr(stats, "penalties_per_18")
        assert stats.penalties_per_18 == DrivingStatsService.DRIVES_PER_18

    def test_rough_per_18_no_holes(self):
        user = UserFactory()
        service = DrivingStatsService()
        assert service.rough_per_18(user) == 0.0

    def test_rough_per_18_no_rough(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with fairway second shot
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=10)

        # Par 5 hole with fairway second shot
        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=250)
        ShotFactory(user=user, hole=hole2, number=3, lie="green", start_distance=100)

        assert service.rough_per_18(user) == 0.0

    def test_rough_per_18_with_rough(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with rough second shot
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="rough", start_distance=200)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=50)

        # Par 5 hole with rough second shot
        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="rough", start_distance=300)
        ShotFactory(user=user, hole=hole2, number=3, lie="green", start_distance=100)

        # Par 4 hole with fairway second shot (no rough)
        hole3 = HoleFactory(user=user, round=round, par=4, number=3)
        ShotFactory(user=user, hole=hole3, number=1, lie="tee", start_distance=380)
        ShotFactory(user=user, hole=hole3, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole3, number=3, lie="green", start_distance=10)

        # Par 3 hole with rough (should be ignored)
        hole4 = HoleFactory(user=user, round=round, par=3, number=4)
        ShotFactory(user=user, hole=hole4, number=1, lie="tee", start_distance=180)
        ShotFactory(user=user, hole=hole4, number=2, lie="rough", start_distance=50)

        # 2 rough holes out of 3 par 4/5 holes
        # Expected: (2/3) * 18 = 12.0
        expected_rough = (2 / 3) * DrivingStatsService.DRIVES_PER_18
        assert service.rough_per_18(user) == pytest.approx(expected_rough)

    def test_rough_per_18_partial_round(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Only 2 holes played, 1 with rough
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="rough", start_distance=200)

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=250)

        # 1 rough hole out of 2 par 4/5 holes
        # Expected: (1/2) * 14 = 7
        expected_rough = (1 / 2) * DrivingStatsService.DRIVES_PER_18
        assert service.rough_per_18(user) == pytest.approx(expected_rough)

    def test_get_for_user_includes_rough(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with rough second shot
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="rough", start_distance=200)

        stats = service.get_for_user(user)

        # Should have rough_per_18 field populated
        assert hasattr(stats, "rough_per_18")
        assert stats.rough_per_18 == DrivingStatsService.DRIVES_PER_18

    def test_fairways_per_18_no_holes(self):
        user = UserFactory()
        service = DrivingStatsService()
        assert service.fairways_per_18(user) == 0.0

    def test_fairways_per_18_no_fairways(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with rough second shot
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="rough", start_distance=200)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=50)

        # Par 5 hole with penalty second shot
        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="penalty", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=3, lie="fairway", start_distance=300)

        assert service.fairways_per_18(user) == 0.0

    def test_fairways_per_18_with_fairways(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with fairway second shot
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)
        ShotFactory(user=user, hole=hole1, number=3, lie="green", start_distance=10)

        # Par 5 hole with fairway second shot
        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="fairway", start_distance=250)
        ShotFactory(user=user, hole=hole2, number=3, lie="green", start_distance=100)

        # Par 4 hole with rough second shot (no fairway)
        hole3 = HoleFactory(user=user, round=round, par=4, number=3)
        ShotFactory(user=user, hole=hole3, number=1, lie="tee", start_distance=380)
        ShotFactory(user=user, hole=hole3, number=2, lie="rough", start_distance=200)
        ShotFactory(user=user, hole=hole3, number=3, lie="green", start_distance=50)

        # Par 3 hole with fairway (should be ignored)
        hole4 = HoleFactory(user=user, round=round, par=3, number=4)
        ShotFactory(user=user, hole=hole4, number=1, lie="tee", start_distance=180)
        ShotFactory(user=user, hole=hole4, number=2, lie="fairway", start_distance=10)

        # 2 fairway holes out of 3 par 4/5 holes
        # Expected: (2/3) * 18 = 12.0
        expected_fairways = (2 / 3) * DrivingStatsService.DRIVES_PER_18
        assert service.fairways_per_18(user) == pytest.approx(expected_fairways)

    def test_fairways_per_18_partial_round(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Only 2 holes played, 1 with fairway
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(user=user, hole=hole2, number=1, lie="tee", start_distance=550)
        ShotFactory(user=user, hole=hole2, number=2, lie="rough", start_distance=300)

        # 1 fairway hole out of 2 par 4/5 holes
        # Expected: (1/2) * 18 = 9.0
        expected_fairways = (1 / 2) * DrivingStatsService.DRIVES_PER_18
        assert service.fairways_per_18(user) == pytest.approx(expected_fairways)

    def test_get_for_user_includes_fairways(self):
        user = UserFactory()
        service = DrivingStatsService()
        round = RoundFactory(user=user)

        # Par 4 hole with fairway second shot
        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(user=user, hole=hole1, number=1, lie="tee", start_distance=400)
        ShotFactory(user=user, hole=hole1, number=2, lie="fairway", start_distance=150)

        stats = service.get_for_user(user)

        # Should have fairways_per_18 field populated
        assert hasattr(stats, "fairways_per_18")
        assert stats.fairways_per_18 == DrivingStatsService.DRIVES_PER_18
