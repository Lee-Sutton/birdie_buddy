from typing import NamedTuple

from birdie_buddy.round_entry.services.proximity_calculator import ProximityCalculator


class ShortGameStats(NamedTuple):
    avg_proximity_0_10_fairway: float
    avg_proximity_0_10_rough: float
    avg_proximity_10_20_fairway: float
    avg_proximity_10_20_rough: float
    avg_proximity_20_30_fairway: float
    avg_proximity_20_30_rough: float
    avg_proximity_sand: float


class ShortGameService:
    def __init__(self):
        self.proximity_calculator = ProximityCalculator()

    def avg_proximity_0_10_fairway(self, user):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "around_green", 0, 10, lie="fairway"
        )

    def avg_proximity_0_10_rough(self, user):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "around_green", 0, 10, lie="rough"
        )

    def avg_proximity_10_20_fairway(self, user):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "around_green", 10, 20, lie="fairway"
        )

    def avg_proximity_10_20_rough(self, user):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "around_green", 10, 20, lie="rough"
        )

    def avg_proximity_20_30_fairway(self, user):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "around_green", 20, 30, lie="fairway"
        )

    def avg_proximity_20_30_rough(self, user):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "around_green", 20, 30, lie="rough"
        )

    def avg_proximity_sand(self, user):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "around_green", 0, None, lie="sand"
        )

    def get_for_user(self, user):
        return ShortGameStats(
            avg_proximity_0_10_fairway=self.avg_proximity_0_10_fairway(user),
            avg_proximity_0_10_rough=self.avg_proximity_0_10_rough(user),
            avg_proximity_10_20_fairway=self.avg_proximity_10_20_fairway(user),
            avg_proximity_10_20_rough=self.avg_proximity_10_20_rough(user),
            avg_proximity_20_30_fairway=self.avg_proximity_20_30_fairway(user),
            avg_proximity_20_30_rough=self.avg_proximity_20_30_rough(user),
            avg_proximity_sand=self.avg_proximity_sand(user),
        )
