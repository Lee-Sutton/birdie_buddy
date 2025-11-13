import pytest

from birdie_buddy.round_entry.factories import HoleFactory, RoundFactory
from birdie_buddy.users.factories import UserFactory
from birdie_buddy.round_entry.services.mental_scorecard_service import (
    MentalScorecardService,
)


@pytest.mark.django_db
class TestMentalScorecardService:
    def test_get_for_round_no_mental_data(self):
        user = UserFactory()
        service = MentalScorecardService()
        round = RoundFactory(user=user)

        HoleFactory(user=user, round=round, par=4, number=1, score=5, mental_scorecard=None)
        HoleFactory(user=user, round=round, par=4, number=2, score=4, mental_scorecard=None)

        stats = service.get_for_round(round)

        assert stats.total_mental_scorecard == 0.0
        assert stats.total_actual_score == 0.0
        assert stats.mental_vs_actual_pct == 0.0
        assert stats.holes_with_mental_data == 0

    def test_get_for_round_with_mental_data(self):
        user = UserFactory()
        service = MentalScorecardService()
        round = RoundFactory(user=user)

        HoleFactory(
            user=user, round=round, par=4, number=1, score=5, mental_scorecard=4
        )
        HoleFactory(
            user=user, round=round, par=4, number=2, score=4, mental_scorecard=3
        )
        HoleFactory(
            user=user, round=round, par=3, number=3, score=3, mental_scorecard=3
        )

        stats = service.get_for_round(round)

        assert stats.total_mental_scorecard == 10.0
        assert stats.total_actual_score == 12.0
        assert stats.mental_vs_actual_pct == pytest.approx((10 / 12) * 100)
        assert stats.holes_with_mental_data == 3

    def test_get_for_round_partial_mental_data(self):
        user = UserFactory()
        service = MentalScorecardService()
        round = RoundFactory(user=user)

        HoleFactory(
            user=user, round=round, par=4, number=1, score=5, mental_scorecard=4
        )
        HoleFactory(user=user, round=round, par=4, number=2, score=4, mental_scorecard=None)
        HoleFactory(
            user=user, round=round, par=3, number=3, score=3, mental_scorecard=2
        )

        stats = service.get_for_round(round)

        assert stats.total_mental_scorecard == 6.0
        assert stats.total_actual_score == 8.0
        assert stats.mental_vs_actual_pct == pytest.approx((6 / 8) * 100)
        assert stats.holes_with_mental_data == 2

    def test_get_for_round_only_returns_data_for_specific_round(self):
        user = UserFactory()
        service = MentalScorecardService()
        round1 = RoundFactory(user=user)
        round2 = RoundFactory(user=user)

        HoleFactory(
            user=user, round=round1, par=4, number=1, score=5, mental_scorecard=4
        )
        HoleFactory(
            user=user, round=round1, par=4, number=2, score=4, mental_scorecard=3
        )

        HoleFactory(
            user=user, round=round2, par=4, number=1, score=6, mental_scorecard=5
        )

        stats = service.get_for_round(round1)

        assert stats.total_mental_scorecard == 7.0
        assert stats.total_actual_score == 9.0
        assert stats.mental_vs_actual_pct == pytest.approx((7 / 9) * 100)
        assert stats.holes_with_mental_data == 2
