from typing import NamedTuple

from django.db.models import Count, Sum

from birdie_buddy.round_entry.models import Hole, Shot
from birdie_buddy.round_entry.services.proximity_calculator import ProximityCalculator


class ShortGameStats(NamedTuple):
    avg_proximity_0_10_fairway: float
    avg_proximity_0_10_rough: float
    avg_proximity_10_20_fairway: float
    avg_proximity_10_20_rough: float
    avg_proximity_20_30_fairway: float
    avg_proximity_20_30_rough: float
    avg_proximity_sand: float
    two_chip_pct_0_10_fairway: float
    two_chip_pct_0_10_rough: float
    two_chip_pct_10_20_fairway: float
    two_chip_pct_10_20_rough: float
    two_chip_pct_20_30_fairway: float
    two_chip_pct_20_30_rough: float
    two_chip_pct_sand: float
    strokes_gained_0_10_fairway_per_18: float
    strokes_gained_0_10_rough_per_18: float
    strokes_gained_10_20_fairway_per_18: float
    strokes_gained_10_20_rough_per_18: float
    strokes_gained_20_30_fairway_per_18: float
    strokes_gained_20_30_rough_per_18: float
    strokes_gained_sand_per_18: float


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

    def two_chip_pct_by_distance_and_lie(
        self, user, min_distance: int, max_distance: int | None, lie: str
    ) -> float:
        filters = {
            "user": user,
            "shot_type": "around_green",
            "start_distance__gte": min_distance,
            "lie": lie,
        }

        if max_distance is not None:
            filters["start_distance__lt"] = max_distance

        holes_with_chips = (
            Shot.objects.filter(**filters)
            .values("hole")
            .annotate(chip_count=Count("id"))
        )

        total_holes = holes_with_chips.count()
        if total_holes == 0:
            return 0.0

        two_chip_holes = holes_with_chips.filter(chip_count__gte=2).count()

        return (two_chip_holes / total_holes) * 100

    def two_chip_pct_0_10_fairway(self, user):
        return self.two_chip_pct_by_distance_and_lie(user, 0, 10, "fairway")

    def two_chip_pct_0_10_rough(self, user):
        return self.two_chip_pct_by_distance_and_lie(user, 0, 10, "rough")

    def two_chip_pct_10_20_fairway(self, user):
        return self.two_chip_pct_by_distance_and_lie(user, 10, 20, "fairway")

    def two_chip_pct_10_20_rough(self, user):
        return self.two_chip_pct_by_distance_and_lie(user, 10, 20, "rough")

    def two_chip_pct_20_30_fairway(self, user):
        return self.two_chip_pct_by_distance_and_lie(user, 20, 30, "fairway")

    def two_chip_pct_20_30_rough(self, user):
        return self.two_chip_pct_by_distance_and_lie(user, 20, 30, "rough")

    def two_chip_pct_sand(self, user):
        return self.two_chip_pct_by_distance_and_lie(user, 0, None, "sand")

    def strokes_gained_by_distance_and_lie(
        self, user, min_distance: int, max_distance: int | None, lie: str
    ) -> float:
        filters = {
            "user": user,
            "shot_type": "around_green",
            "start_distance__gte": min_distance,
            "lie": lie,
        }

        if max_distance is not None:
            filters["start_distance__lt"] = max_distance

        shots = Shot.objects.filter(**filters)
        total_sg = shots.aggregate(total=Sum("strokes_gained"))["total"] or 0.0

        total_holes = Hole.objects.filter(user=user).count()
        if total_holes == 0:
            return 0.0

        return (total_sg / total_holes) * 18

    def strokes_gained_0_10_fairway(self, user):
        return self.strokes_gained_by_distance_and_lie(user, 0, 10, "fairway")

    def strokes_gained_0_10_rough(self, user):
        return self.strokes_gained_by_distance_and_lie(user, 0, 10, "rough")

    def strokes_gained_10_20_fairway(self, user):
        return self.strokes_gained_by_distance_and_lie(user, 10, 20, "fairway")

    def strokes_gained_10_20_rough(self, user):
        return self.strokes_gained_by_distance_and_lie(user, 10, 20, "rough")

    def strokes_gained_20_30_fairway(self, user):
        return self.strokes_gained_by_distance_and_lie(user, 20, 30, "fairway")

    def strokes_gained_20_30_rough(self, user):
        return self.strokes_gained_by_distance_and_lie(user, 20, 30, "rough")

    def strokes_gained_sand(self, user):
        return self.strokes_gained_by_distance_and_lie(user, 0, None, "sand")

    def get_for_user(self, user):
        return ShortGameStats(
            avg_proximity_0_10_fairway=self.avg_proximity_0_10_fairway(user),
            avg_proximity_0_10_rough=self.avg_proximity_0_10_rough(user),
            avg_proximity_10_20_fairway=self.avg_proximity_10_20_fairway(user),
            avg_proximity_10_20_rough=self.avg_proximity_10_20_rough(user),
            avg_proximity_20_30_fairway=self.avg_proximity_20_30_fairway(user),
            avg_proximity_20_30_rough=self.avg_proximity_20_30_rough(user),
            avg_proximity_sand=self.avg_proximity_sand(user),
            two_chip_pct_0_10_fairway=self.two_chip_pct_0_10_fairway(user),
            two_chip_pct_0_10_rough=self.two_chip_pct_0_10_rough(user),
            two_chip_pct_10_20_fairway=self.two_chip_pct_10_20_fairway(user),
            two_chip_pct_10_20_rough=self.two_chip_pct_10_20_rough(user),
            two_chip_pct_20_30_fairway=self.two_chip_pct_20_30_fairway(user),
            two_chip_pct_20_30_rough=self.two_chip_pct_20_30_rough(user),
            two_chip_pct_sand=self.two_chip_pct_sand(user),
            strokes_gained_0_10_fairway_per_18=self.strokes_gained_0_10_fairway(user),
            strokes_gained_0_10_rough_per_18=self.strokes_gained_0_10_rough(user),
            strokes_gained_10_20_fairway_per_18=self.strokes_gained_10_20_fairway(user),
            strokes_gained_10_20_rough_per_18=self.strokes_gained_10_20_rough(user),
            strokes_gained_20_30_fairway_per_18=self.strokes_gained_20_30_fairway(user),
            strokes_gained_20_30_rough_per_18=self.strokes_gained_20_30_rough(user),
            strokes_gained_sand_per_18=self.strokes_gained_sand(user),
        )
