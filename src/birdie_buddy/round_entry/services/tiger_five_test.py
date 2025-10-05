import pytest
from birdie_buddy.round_entry.services.tiger_five import TigerFiveService
from birdie_buddy.round_entry.factories import (
    RoundFactory,
    HoleFactory,
    full_round_factory,
)
from birdie_buddy.round_entry.factories.shot_factory import ShotFactory


@pytest.mark.django_db
def test_tiger_five_no_holes():
    round_obj = RoundFactory()
    user = round_obj.user
    service = TigerFiveService()
    result = service.get_for_user(user)
    assert result.penalties == 0
    assert result.double_bogeys == 0
    assert result.three_putts == 0
    assert result.bogeys_inside_150 == 0
    assert result.two_chip == 0


@pytest.mark.django_db
def test_tiger_five_basic_counts():
    # Create a single round with a few crafted holes
    round = RoundFactory(holes_played=4)
    user = round.user

    # Hole 1: penalty on the hole
    h1 = HoleFactory(par=4, round=round, user=user)
    ShotFactory(hole=h1, user=user, start_distance=300, lie="tee")
    ShotFactory(hole=h1, user=user, start_distance=100, lie="fairway")
    ShotFactory(hole=h1, user=user, start_distance=20, lie="penalty")
    h1.score = 5
    h1.save()

    # Hole 2: double bogey
    h2 = HoleFactory(par=4, round=round, user=user)
    ShotFactory(hole=h2, user=user, start_distance=400, lie="tee")
    ShotFactory(hole=h2, user=user, start_distance=200, lie="rough")
    ShotFactory(hole=h2, user=user, start_distance=50, lie="rough")
    ShotFactory(hole=h2, user=user, start_distance=10, lie="green")
    h2.score = 6
    h2.save()

    # Hole 3: three-putt
    h3 = HoleFactory(par=3, round=round, user=user)
    ShotFactory(hole=h3, user=user, start_distance=170, lie="tee")
    ShotFactory(hole=h3, user=user, start_distance=20, lie="green")
    ShotFactory(hole=h3, user=user, start_distance=5, lie="green")
    ShotFactory(hole=h3, user=user, start_distance=1, lie="green")
    h3.score = 4
    h3.save()

    # Hole 4: bogey from inside 150 and two-chip
    h4 = HoleFactory(par=4, round=round, user=user)
    ShotFactory(hole=h4, user=user, start_distance=400, lie="tee")
    ShotFactory(hole=h4, user=user, start_distance=120, lie="fairway")
    # two short-game shots
    ShotFactory(hole=h4, user=user, start_distance=30, lie="sand")
    ShotFactory(hole=h4, user=user, start_distance=20, lie="fairway")
    ShotFactory(hole=h4, user=user, start_distance=2, lie="green")
    h4.score = 5
    h4.save()

    service = TigerFiveService()
    result = service.get_for_user(user)

    # We created 4 holes, so counts should scale to per-18 holes
    scale = 18 / 4
    assert result.penalties == pytest.approx(1 * scale)
    assert result.double_bogeys == pytest.approx(1 * scale)
    assert result.three_putts == pytest.approx(1 * scale)
    assert result.bogeys_inside_150 == pytest.approx(1 * scale)
    assert result.two_chip == pytest.approx(1 * scale)
