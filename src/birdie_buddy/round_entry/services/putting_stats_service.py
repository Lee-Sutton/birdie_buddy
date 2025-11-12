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


class RoundPuttingStats(NamedTuple):
    make_rate_0_3: float
    make_rate_3_6: float
    make_rate_6_9: float
    make_rate_9_12: float
    make_rate_12_15: float
    make_rate_15_20: float
    make_rate_20_30: float
    make_rate_30_40: float
    make_rate_40_plus: float
    strokes_gained_0_3: float
    strokes_gained_3_6: float
    strokes_gained_6_9: float
    strokes_gained_9_12: float
    strokes_gained_12_15: float
    strokes_gained_15_20: float
    strokes_gained_20_30: float
    strokes_gained_30_40: float
    strokes_gained_40_plus: float


class PuttingStatsService:
    def _get_make_rate_for_distance(
        self, user, min_feet: int, max_feet: int | None, round=None
    ) -> float:
        putts = Shot.objects.filter(user=user, shot_type="putt", feet__gte=min_feet)

        if max_feet:
            putts = putts.filter(feet__lt=max_feet)

        if round is not None:
            putts = putts.filter(hole__round=round)

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
        self, user, min_feet: int, max_feet: int | None, round=None
    ) -> float:
        filters = {
            "user": user,
            "shot_type": "putt",
            "feet__gte": min_feet,
        }

        if max_feet is not None:
            filters["feet__lt"] = max_feet

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

    def make_rate_0_3(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 0, 3, round)

    def make_rate_3_6(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 3, 6, round)

    def make_rate_6_9(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 6, 9, round)

    def make_rate_9_12(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 9, 12, round)

    def make_rate_12_15(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 12, 15, round)

    def make_rate_15_20(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 15, 20, round)

    def make_rate_20_30(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 20, 30, round)

    def make_rate_30_40(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 30, 40, round)

    def make_rate_40_plus(self, user, round=None) -> float:
        return self._get_make_rate_for_distance(user, 40, None, round)

    def strokes_gained_0_3(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 0, 3, round)

    def strokes_gained_3_6(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 3, 6, round)

    def strokes_gained_6_9(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 6, 9, round)

    def strokes_gained_9_12(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 9, 12, round)

    def strokes_gained_12_15(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 12, 15, round)

    def strokes_gained_15_20(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 15, 20, round)

    def strokes_gained_20_30(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 20, 30, round)

    def strokes_gained_30_40(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 30, 40, round)

    def strokes_gained_40_plus(self, user, round=None) -> float:
        return self._get_strokes_gained_for_distance(user, 40, None, round)

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

    def get_for_round(self, round) -> RoundPuttingStats:
        user = round.user
        return RoundPuttingStats(
            make_rate_0_3=self.make_rate_0_3(user, round),
            make_rate_3_6=self.make_rate_3_6(user, round),
            make_rate_6_9=self.make_rate_6_9(user, round),
            make_rate_9_12=self.make_rate_9_12(user, round),
            make_rate_12_15=self.make_rate_12_15(user, round),
            make_rate_15_20=self.make_rate_15_20(user, round),
            make_rate_20_30=self.make_rate_20_30(user, round),
            make_rate_30_40=self.make_rate_30_40(user, round),
            make_rate_40_plus=self.make_rate_40_plus(user, round),
            strokes_gained_0_3=self.strokes_gained_0_3(user, round),
            strokes_gained_3_6=self.strokes_gained_3_6(user, round),
            strokes_gained_6_9=self.strokes_gained_6_9(user, round),
            strokes_gained_9_12=self.strokes_gained_9_12(user, round),
            strokes_gained_12_15=self.strokes_gained_12_15(user, round),
            strokes_gained_15_20=self.strokes_gained_15_20(user, round),
            strokes_gained_20_30=self.strokes_gained_20_30(user, round),
            strokes_gained_30_40=self.strokes_gained_30_40(user, round),
            strokes_gained_40_plus=self.strokes_gained_40_plus(user, round),
        )
