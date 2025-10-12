import pytest

from birdie_buddy.round_entry.factories import (
    HoleFactory,
    RoundFactory,
    ShotFactory,
)

from birdie_buddy.users.factories import UserFactory

from birdie_buddy.round_entry.services.approach_stats_service import (
    ApproachShotService,
)


@pytest.mark.django_db
class TestApproachShotService:
    def test_strokes_gained_30_100_no_holes(self):
        user = UserFactory()
        service = ApproachShotService()
        assert service.strokes_gained_30_100(user) == 0.0

    def test_strokes_gained_30_100_no_approach_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole,
            number=2,
            lie="green",
            start_distance=10,
            strokes_gained=-0.1,
        )

        assert service.strokes_gained_30_100(user) == 0.0

    def test_strokes_gained_30_100_with_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=80,
            strokes_gained=0.5,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=380,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="rough",
            start_distance=90,
            strokes_gained=-0.3,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="green",
            start_distance=15,
            strokes_gained=0.2,
        )

        expected_sg = ((0.5 + (-0.3)) / 2) * 18
        assert service.strokes_gained_30_100(user) == pytest.approx(expected_sg)

    def test_strokes_gained_100_150_no_holes(self):
        user = UserFactory()
        service = ApproachShotService()
        assert service.strokes_gained_100_150(user) == 0.0

    def test_strokes_gained_100_150_with_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=120,
            strokes_gained=0.4,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=550,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=280,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="fairway",
            start_distance=140,
            strokes_gained=-0.2,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            lie="green",
            start_distance=5,
            strokes_gained=0.0,
        )

        expected_sg = ((0.4 + (-0.2)) / 2) * 18
        assert service.strokes_gained_100_150(user) == pytest.approx(expected_sg)

    def test_strokes_gained_150_200_no_holes(self):
        user = UserFactory()
        service = ApproachShotService()
        assert service.strokes_gained_150_200(user) == 0.0

    def test_strokes_gained_150_200_with_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=180,
            strokes_gained=0.6,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=8,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=550,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=280,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="rough",
            start_distance=170,
            strokes_gained=-0.4,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            lie="green",
            start_distance=10,
            strokes_gained=0.0,
        )

        expected_sg = ((0.6 + (-0.4)) / 2) * 18
        assert service.strokes_gained_150_200(user) == pytest.approx(expected_sg)

    def test_strokes_gained_over_200_no_holes(self):
        user = UserFactory()
        service = ApproachShotService()
        assert service.strokes_gained_over_200(user) == 0.0

    def test_strokes_gained_over_200_with_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=220,
            strokes_gained=0.7,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=5,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=550,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=280,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="tee",
            start_distance=240,
            strokes_gained=-0.5,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            lie="green",
            start_distance=8,
            strokes_gained=0.0,
        )

        expected_sg = ((0.7 + (-0.5)) / 2) * 18
        assert service.strokes_gained_over_200(user) == pytest.approx(expected_sg)

    def test_strokes_gained_excludes_non_approach_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole,
            number=2,
            lie="fairway",
            start_distance=120,
            strokes_gained=0.5,
        )
        ShotFactory(
            user=user,
            hole=hole,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=-0.1,
        )

        expected_sg = (0.5 / 1) * 18
        assert service.strokes_gained_100_150(user) == pytest.approx(expected_sg)

    def test_get_for_user_returns_all_stats(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="fairway",
            start_distance=80,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=550,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=280,
            strokes_gained=0.0,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="fairway",
            start_distance=120,
            strokes_gained=0.4,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            lie="green",
            start_distance=5,
            strokes_gained=0.2,
        )

        stats = service.get_for_user(user)

        assert hasattr(stats, "strokes_gained_30_100_per_18")
        assert hasattr(stats, "strokes_gained_100_150_per_18")
        assert hasattr(stats, "strokes_gained_150_200_per_18")
        assert hasattr(stats, "strokes_gained_over_200_per_18")

        expected_30_100 = (0.3 / 2) * 18
        expected_100_150 = (0.4 / 2) * 18

        assert stats.strokes_gained_30_100_per_18 == pytest.approx(expected_30_100)
        assert stats.strokes_gained_100_150_per_18 == pytest.approx(expected_100_150)
        assert stats.strokes_gained_150_200_per_18 == 0.0
        assert stats.strokes_gained_over_200_per_18 == 0.0

    def test_strokes_gained_30_100_rough_no_holes(self):
        user = UserFactory()
        service = ApproachShotService()
        assert service.strokes_gained_30_100_rough(user) == 0.0

    def test_strokes_gained_30_100_rough_with_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="rough",
            start_distance=80,
            strokes_gained=-0.4,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=4, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=380,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="rough",
            start_distance=90,
            strokes_gained=-0.2,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="green",
            start_distance=15,
            strokes_gained=0.2,
        )

        hole3 = HoleFactory(user=user, round=round, par=4, number=3)
        ShotFactory(
            user=user,
            hole=hole3,
            number=1,
            lie="tee",
            start_distance=390,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=2,
            lie="fairway",
            start_distance=85,
            strokes_gained=0.5,
        )
        ShotFactory(
            user=user,
            hole=hole3,
            number=3,
            lie="green",
            start_distance=12,
            strokes_gained=0.1,
        )

        expected_sg = ((-0.4 + (-0.2)) / 3) * 18
        assert service.strokes_gained_30_100_rough(user) == pytest.approx(expected_sg)

    def test_strokes_gained_100_150_rough_with_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="rough",
            start_distance=120,
            strokes_gained=-0.3,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=550,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=280,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="rough",
            start_distance=140,
            strokes_gained=-0.5,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            lie="green",
            start_distance=5,
            strokes_gained=0.0,
        )

        expected_sg = ((-0.3 + (-0.5)) / 2) * 18
        assert service.strokes_gained_100_150_rough(user) == pytest.approx(expected_sg)

    def test_strokes_gained_150_200_rough_with_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="rough",
            start_distance=180,
            strokes_gained=-0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=8,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=550,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=280,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="rough",
            start_distance=170,
            strokes_gained=-0.6,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            lie="green",
            start_distance=10,
            strokes_gained=0.0,
        )

        expected_sg = ((-0.2 + (-0.6)) / 2) * 18
        assert service.strokes_gained_150_200_rough(user) == pytest.approx(expected_sg)

    def test_strokes_gained_over_200_rough_with_shots(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="rough",
            start_distance=220,
            strokes_gained=-0.1,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=5,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=550,
            strokes_gained=0.3,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=280,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="rough",
            start_distance=240,
            strokes_gained=-0.7,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            lie="green",
            start_distance=8,
            strokes_gained=0.0,
        )

        expected_sg = ((-0.1 + (-0.7)) / 2) * 18
        assert service.strokes_gained_over_200_rough(user) == pytest.approx(expected_sg)

    def test_get_for_user_returns_all_stats_including_rough(self):
        user = UserFactory()
        service = ApproachShotService()
        round = RoundFactory(user=user)

        hole1 = HoleFactory(user=user, round=round, par=4, number=1)
        ShotFactory(
            user=user,
            hole=hole1,
            number=1,
            lie="tee",
            start_distance=400,
            strokes_gained=0.2,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=2,
            lie="rough",
            start_distance=80,
            strokes_gained=-0.3,
        )
        ShotFactory(
            user=user,
            hole=hole1,
            number=3,
            lie="green",
            start_distance=10,
            strokes_gained=-0.1,
        )

        hole2 = HoleFactory(user=user, round=round, par=5, number=2)
        ShotFactory(
            user=user,
            hole=hole2,
            number=1,
            lie="tee",
            start_distance=550,
            strokes_gained=0.1,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=2,
            lie="fairway",
            start_distance=280,
            strokes_gained=0.0,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=3,
            lie="rough",
            start_distance=120,
            strokes_gained=-0.4,
        )
        ShotFactory(
            user=user,
            hole=hole2,
            number=4,
            lie="green",
            start_distance=5,
            strokes_gained=0.2,
        )

        stats = service.get_for_user(user)

        assert hasattr(stats, "strokes_gained_30_100_rough_per_18")
        assert hasattr(stats, "strokes_gained_100_150_rough_per_18")
        assert hasattr(stats, "strokes_gained_150_200_rough_per_18")
        assert hasattr(stats, "strokes_gained_over_200_rough_per_18")

        expected_30_100_rough = (-0.3 / 2) * 18
        expected_100_150_rough = (-0.4 / 2) * 18

        assert stats.strokes_gained_30_100_rough_per_18 == pytest.approx(
            expected_30_100_rough
        )
        assert stats.strokes_gained_100_150_rough_per_18 == pytest.approx(
            expected_100_150_rough
        )
        assert stats.strokes_gained_150_200_rough_per_18 == 0.0
        assert stats.strokes_gained_over_200_rough_per_18 == 0.0
