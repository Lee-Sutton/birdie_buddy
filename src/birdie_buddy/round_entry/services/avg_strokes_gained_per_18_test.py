import pytest
from birdie_buddy.round_entry.services.avg_strokes_gained_per_18 import (
    get_avg_strokes_gained_categories_per_18,
)
from birdie_buddy.round_entry.factories import RoundFactory, HoleFactory


@pytest.mark.django_db
def test_avg_strokes_gained_categories_per_18_basic():
    round = RoundFactory()
    user = round.user
    HoleFactory.par_5_par(round=round, user=user)
    HoleFactory.par_4_par(round=round, user=user)
    HoleFactory.par_3_par(round=round, user=user)
    HoleFactory.par_4_missed_green(round=round, user=user)

    result = get_avg_strokes_gained_categories_per_18(user)

    assert pytest.approx(result.driving) == 0.225
    assert pytest.approx(result.approach) == -2.0925
    assert pytest.approx(result.short_game) == 2.07
    assert pytest.approx(result.putting) == -1.98


@pytest.mark.django_db
def test_avg_strokes_gained_categories_per_18_no_holes():
    round_obj = RoundFactory()
    user = round_obj.user
    result = get_avg_strokes_gained_categories_per_18(user)
    assert result.driving == 0
    assert result.approach == 0
    assert result.short_game == 0
    assert result.putting == 0
    user = round_obj.user
    result = get_avg_strokes_gained_categories_per_18(user)
    assert result.driving == 0
    assert result.approach == 0
    assert result.short_game == 0
    assert result.putting == 0
