from typing import NamedTuple

from django.db.models import F, Sum, Window
from django.db.models.functions import Lead

from birdie_buddy.round_entry.models import Hole, Shot


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
    def _strokes_gained_by_distance_range(
        self, user, min_distance: int, max_distance: int | None, lie: str | None = None
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

        shots = Shot.objects.filter(**filters)
        total_sg = shots.aggregate(total=Sum("strokes_gained"))["total"] or 0.0

        total_holes = Hole.objects.filter(user=user).count()
        if total_holes == 0:
            return 0.0

        return (total_sg / total_holes) * 18

    def strokes_gained_30_100(self, user):
        return self._strokes_gained_by_distance_range(user, 30, 100)

    def strokes_gained_100_150(self, user):
        return self._strokes_gained_by_distance_range(user, 100, 150)

    def strokes_gained_150_200(self, user):
        return self._strokes_gained_by_distance_range(user, 150, 200)

    def strokes_gained_over_200(self, user):
        return self._strokes_gained_by_distance_range(user, 200, None)

    def strokes_gained_30_100_rough(self, user):
        return self._strokes_gained_by_distance_range(user, 30, 100, lie="rough")

    def strokes_gained_100_150_rough(self, user):
        return self._strokes_gained_by_distance_range(user, 100, 150, lie="rough")

    def strokes_gained_150_200_rough(self, user):
        return self._strokes_gained_by_distance_range(user, 150, 200, lie="rough")

    def strokes_gained_over_200_rough(self, user):
        return self._strokes_gained_by_distance_range(user, 200, None, lie="rough")

    def _avg_proximity_by_distance_range(
        self, user, min_distance: int, max_distance: int | None, lie: str | None = None
    ) -> float:
        """TODO: this method is inefficient and could be optimized"""
        shots_with_next = Shot.objects.filter(user=user).annotate(
            next_distance=Window(
                expression=Lead("start_distance"),
                partition_by=[F("hole_id")],
                order_by=F("id").asc(),
            )
        )

        proximities = []
        for shot in shots_with_next:
            if (
                shot.shot_type == "approach"
                and shot.start_distance >= min_distance
                and (max_distance is None or shot.start_distance < max_distance)
                and (lie is None or shot.lie == lie)
                and shot.next_distance is not None
            ):
                proximities.append(shot.next_distance)

        if not proximities:
            return 0.0

        return sum(proximities) / len(proximities)

    def avg_proximity_30_100(self, user):
        return self._avg_proximity_by_distance_range(user, 30, 100)

    def avg_proximity_100_150(self, user):
        return self._avg_proximity_by_distance_range(user, 100, 150)

    def avg_proximity_150_200(self, user):
        return self._avg_proximity_by_distance_range(user, 150, 200)

    def avg_proximity_over_200(self, user):
        return self._avg_proximity_by_distance_range(user, 200, None)

    def avg_proximity_30_100_rough(self, user):
        return self._avg_proximity_by_distance_range(user, 30, 100, lie="rough")

    def avg_proximity_100_150_rough(self, user):
        return self._avg_proximity_by_distance_range(user, 100, 150, lie="rough")

    def avg_proximity_150_200_rough(self, user):
        return self._avg_proximity_by_distance_range(user, 150, 200, lie="rough")

    def avg_proximity_over_200_rough(self, user):
        return self._avg_proximity_by_distance_range(user, 200, None, lie="rough")

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
