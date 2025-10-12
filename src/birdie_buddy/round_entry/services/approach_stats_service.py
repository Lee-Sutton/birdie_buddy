from typing import NamedTuple

from django.db.models import Sum

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


class ApproachShotService:
    def _strokes_gained_by_distance_range(self, user, min_distance: int, max_distance: int | None, lie: str | None = None) -> float:
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

    def get_for_user(self, user):
        return ApproachStats(
            strokes_gained_30_100_per_18=self.strokes_gained_30_100(user),
            strokes_gained_100_150_per_18=self.strokes_gained_100_150(user),
            strokes_gained_150_200_per_18=self.strokes_gained_150_200(user),
            strokes_gained_over_200_per_18=self.strokes_gained_over_200(user),
            strokes_gained_30_100_rough_per_18=self.strokes_gained_30_100_rough(user),
            strokes_gained_100_150_rough_per_18=self.strokes_gained_100_150_rough(user),
            strokes_gained_150_200_rough_per_18=self.strokes_gained_150_200_rough(user),
            strokes_gained_over_200_rough_per_18=self.strokes_gained_over_200_rough(user),
        )
