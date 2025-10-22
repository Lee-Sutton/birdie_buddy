from typing import NamedTuple
from django.db.models import Max, Sum

from birdie_buddy.round_entry.models import Shot, Hole


class PuttingStats(NamedTuple):
    make_rate_0_3: float
    make_rate_3_6: float
    make_rate_6_9: float
    make_rate_9_12: float
    make_rate_12_15: float
    make_rate_15_20: float
    make_rate_20_30: float
    make_rate_30_40: float
    make_rate_40_plus: float
    strokes_gained_0_3_per_18: float
    strokes_gained_3_6_per_18: float
    strokes_gained_6_9_per_18: float
    strokes_gained_9_12_per_18: float
    strokes_gained_12_15_per_18: float
    strokes_gained_15_20_per_18: float
    strokes_gained_20_30_per_18: float
    strokes_gained_30_40_per_18: float
    strokes_gained_40_plus_per_18: float


class PuttingStatsService:
    def _get_make_rate_for_distance(
        self, user, min_feet: int, max_feet: int | None
    ) -> float:
        putts = Shot.objects.filter(user=user, shot_type="putt", feet__gte=min_feet)

        if max_feet:
            putts = putts.filter(feet__lt=max_feet)

        total_putts = putts.count()

        if total_putts == 0:
            return 0.0

        made_putts = 0
        for putt in putts.select_related("hole"):
            max_shot_number = putt.hole.shot_set.aggregate(Max("number"))["number__max"]
            if putt.number == max_shot_number:
                made_putts += 1

        return (made_putts / total_putts) * 100

    def _get_strokes_gained_for_distance(
        self, user, min_feet: int, max_feet: int | None
    ) -> float:
        filters = {
            "user": user,
            "shot_type": "putt",
            "feet__gte": min_feet,
        }

        if max_feet is not None:
            filters["feet__lt"] = max_feet

        shots = Shot.objects.filter(**filters)
        total_sg = shots.aggregate(total=Sum("strokes_gained"))["total"] or 0.0

        total_holes = Hole.objects.filter(user=user).count()
        if total_holes == 0:
            return 0.0

        return (total_sg / total_holes) * 18

    def make_rate_0_3(self, user) -> float:
        return self._get_make_rate_for_distance(user, 0, 3)

    def make_rate_3_6(self, user) -> float:
        return self._get_make_rate_for_distance(user, 3, 6)

    def make_rate_6_9(self, user) -> float:
        return self._get_make_rate_for_distance(user, 6, 9)

    def make_rate_9_12(self, user) -> float:
        return self._get_make_rate_for_distance(user, 9, 12)

    def make_rate_12_15(self, user) -> float:
        return self._get_make_rate_for_distance(user, 12, 15)

    def make_rate_15_20(self, user) -> float:
        return self._get_make_rate_for_distance(user, 15, 20)

    def make_rate_20_30(self, user) -> float:
        return self._get_make_rate_for_distance(user, 20, 30)

    def make_rate_30_40(self, user) -> float:
        return self._get_make_rate_for_distance(user, 30, 40)

    def make_rate_40_plus(self, user) -> float:
        return self._get_make_rate_for_distance(user, 40, None)

    def strokes_gained_0_3(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 0, 3)

    def strokes_gained_3_6(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 3, 6)

    def strokes_gained_6_9(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 6, 9)

    def strokes_gained_9_12(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 9, 12)

    def strokes_gained_12_15(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 12, 15)

    def strokes_gained_15_20(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 15, 20)

    def strokes_gained_20_30(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 20, 30)

    def strokes_gained_30_40(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 30, 40)

    def strokes_gained_40_plus(self, user) -> float:
        return self._get_strokes_gained_for_distance(user, 40, None)

    def get_for_user(self, user) -> PuttingStats:
        return PuttingStats(
            make_rate_0_3=self.make_rate_0_3(user),
            make_rate_3_6=self.make_rate_3_6(user),
            make_rate_6_9=self.make_rate_6_9(user),
            make_rate_9_12=self.make_rate_9_12(user),
            make_rate_12_15=self.make_rate_12_15(user),
            make_rate_15_20=self.make_rate_15_20(user),
            make_rate_20_30=self.make_rate_20_30(user),
            make_rate_30_40=self.make_rate_30_40(user),
            make_rate_40_plus=self.make_rate_40_plus(user),
            strokes_gained_0_3_per_18=self.strokes_gained_0_3(user),
            strokes_gained_3_6_per_18=self.strokes_gained_3_6(user),
            strokes_gained_6_9_per_18=self.strokes_gained_6_9(user),
            strokes_gained_9_12_per_18=self.strokes_gained_9_12(user),
            strokes_gained_12_15_per_18=self.strokes_gained_12_15(user),
            strokes_gained_15_20_per_18=self.strokes_gained_15_20(user),
            strokes_gained_20_30_per_18=self.strokes_gained_20_30(user),
            strokes_gained_30_40_per_18=self.strokes_gained_30_40(user),
            strokes_gained_40_plus_per_18=self.strokes_gained_40_plus(user),
        )
