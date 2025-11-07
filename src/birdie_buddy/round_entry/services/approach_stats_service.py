from typing import NamedTuple

from django.db.models import Sum

from birdie_buddy.round_entry.models import Hole, Shot
from birdie_buddy.round_entry.services.proximity_calculator import ProximityCalculator


class ApproachStats(NamedTuple):
    strokes_gained_30_100_per_18: float
    strokes_gained_100_150_per_18: float
    strokes_gained_150_200_per_18: float
    strokes_gained_over_200_per_18: float
    strokes_gained_30_100_rough_per_18: float
    strokes_gained_100_150_rough_per_18: float
    strokes_gained_150_200_rough_per_18: float
    strokes_gained_over_200_rough_per_18: float
    avg_proximity_30_100: float
    avg_proximity_100_150: float
    avg_proximity_150_200: float
    avg_proximity_over_200: float
    avg_proximity_30_100_rough: float
    avg_proximity_100_150_rough: float
    avg_proximity_150_200_rough: float
    avg_proximity_over_200_rough: float


class ApproachShotService:
    def __init__(self):
        self.proximity_calculator = ProximityCalculator()

    def strokes_gained_by_distance_range(
        self, user, min_distance: int, max_distance: int | None, lie: str | None = None, round=None
    ) -> float:
        filters = {
            "user": user,
            "shot_type": "approach",
            "start_distance__gte": min_distance,
        }

        if max_distance is not None:
            filters["start_distance__lt"] = max_distance

        if lie is not None:
            filters["lie"] = lie

        if round is not None:
            filters["hole__round"] = round

        shots = Shot.objects.filter(**filters)
        total_sg = shots.aggregate(total=Sum("strokes_gained"))["total"] or 0.0

        if round is not None:
            return total_sg

        total_holes = Hole.objects.filter(user=user).count()
        if total_holes == 0:
            return 0.0

        return (total_sg / total_holes) * 18

    def strokes_gained_30_100(self, user, round=None):
        return self.strokes_gained_by_distance_range(user, 30, 100, round=round)

    def strokes_gained_100_150(self, user, round=None):
        return self.strokes_gained_by_distance_range(user, 100, 150, round=round)

    def strokes_gained_150_200(self, user, round=None):
        return self.strokes_gained_by_distance_range(user, 150, 200, round=round)

    def strokes_gained_over_200(self, user, round=None):
        return self.strokes_gained_by_distance_range(user, 200, None, round=round)

    def strokes_gained_30_100_rough(self, user, round=None):
        return self.strokes_gained_by_distance_range(user, 30, 100, lie="rough", round=round)

    def strokes_gained_100_150_rough(self, user, round=None):
        return self.strokes_gained_by_distance_range(user, 100, 150, lie="rough", round=round)

    def strokes_gained_150_200_rough(self, user, round=None):
        return self.strokes_gained_by_distance_range(user, 150, 200, lie="rough", round=round)

    def strokes_gained_over_200_rough(self, user, round=None):
        return self.strokes_gained_by_distance_range(user, 200, None, lie="rough", round=round)

    def avg_proximity_30_100(self, user, round=None):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "approach", 30, 100, round=round
        )

    def avg_proximity_100_150(self, user, round=None):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "approach", 100, 150, round=round
        )

    def avg_proximity_150_200(self, user, round=None):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "approach", 150, 200, round=round
        )

    def avg_proximity_over_200(self, user, round=None):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "approach", 200, None, round=round
        )

    def avg_proximity_30_100_rough(self, user, round=None):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "approach", 30, 100, lie="rough", round=round
        )

    def avg_proximity_100_150_rough(self, user, round=None):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "approach", 100, 150, lie="rough", round=round
        )

    def avg_proximity_150_200_rough(self, user, round=None):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "approach", 150, 200, lie="rough", round=round
        )

    def avg_proximity_over_200_rough(self, user, round=None):
        return self.proximity_calculator.calculate_avg_proximity(
            user, "approach", 200, None, lie="rough", round=round
        )

    def get_for_user(self, user):
        return ApproachStats(
            strokes_gained_30_100_per_18=self.strokes_gained_30_100(user),
            strokes_gained_100_150_per_18=self.strokes_gained_100_150(user),
            strokes_gained_150_200_per_18=self.strokes_gained_150_200(user),
            strokes_gained_over_200_per_18=self.strokes_gained_over_200(user),
            strokes_gained_30_100_rough_per_18=self.strokes_gained_30_100_rough(user),
            strokes_gained_100_150_rough_per_18=self.strokes_gained_100_150_rough(user),
            strokes_gained_150_200_rough_per_18=self.strokes_gained_150_200_rough(user),
            strokes_gained_over_200_rough_per_18=self.strokes_gained_over_200_rough(
                user
            ),
            avg_proximity_30_100=self.avg_proximity_30_100(user),
            avg_proximity_100_150=self.avg_proximity_100_150(user),
            avg_proximity_150_200=self.avg_proximity_150_200(user),
            avg_proximity_over_200=self.avg_proximity_over_200(user),
            avg_proximity_30_100_rough=self.avg_proximity_30_100_rough(user),
            avg_proximity_100_150_rough=self.avg_proximity_100_150_rough(user),
            avg_proximity_150_200_rough=self.avg_proximity_150_200_rough(user),
            avg_proximity_over_200_rough=self.avg_proximity_over_200_rough(user),
        )

    def get_for_round(self, round):
        return ApproachStats(
            strokes_gained_30_100_per_18=self.strokes_gained_30_100(round.user, round),
            strokes_gained_100_150_per_18=self.strokes_gained_100_150(round.user, round),
            strokes_gained_150_200_per_18=self.strokes_gained_150_200(round.user, round),
            strokes_gained_over_200_per_18=self.strokes_gained_over_200(round.user, round),
            strokes_gained_30_100_rough_per_18=self.strokes_gained_30_100_rough(round.user, round),
            strokes_gained_100_150_rough_per_18=self.strokes_gained_100_150_rough(round.user, round),
            strokes_gained_150_200_rough_per_18=self.strokes_gained_150_200_rough(round.user, round),
            strokes_gained_over_200_rough_per_18=self.strokes_gained_over_200_rough(
                round.user, round
            ),
            avg_proximity_30_100=self.avg_proximity_30_100(round.user, round),
            avg_proximity_100_150=self.avg_proximity_100_150(round.user, round),
            avg_proximity_150_200=self.avg_proximity_150_200(round.user, round),
            avg_proximity_over_200=self.avg_proximity_over_200(round.user, round),
            avg_proximity_30_100_rough=self.avg_proximity_30_100_rough(round.user, round),
            avg_proximity_100_150_rough=self.avg_proximity_100_150_rough(round.user, round),
            avg_proximity_150_200_rough=self.avg_proximity_150_200_rough(round.user, round),
            avg_proximity_over_200_rough=self.avg_proximity_over_200_rough(round.user, round),
        )
