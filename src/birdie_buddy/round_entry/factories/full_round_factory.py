from birdie_buddy.round_entry.factories.hole_factory import HoleFactory
from birdie_buddy.round_entry.factories.round_factory import RoundFactory


def full_round_factory(n_holes=18, **kwargs):
    round = RoundFactory(**kwargs)
    [
        HoleFactory.create_with_shots(number=n + 1, round=round, user=round.user)
        for n in range(n_holes)
    ]

    return round
