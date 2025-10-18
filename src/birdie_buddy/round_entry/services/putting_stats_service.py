from typing import NamedTuple
from django.db.models import Max

from birdie_buddy.round_entry.models import Shot


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
    make_rate_overall: float


# TODO: fix the yards/feet confusion throughout
class PuttingStatsService:
    def _get_make_rate_for_distance(
        self, user, min_feet: int, max_feet: int | None
    ) -> float:
        min_yards = min_feet / 3
        max_yards = max_feet / 3 if max_feet else None

        putts = Shot.objects.filter(
            user=user, shot_type="putt", start_distance__gte=min_yards
        )

        if max_yards:
            putts = putts.filter(start_distance__lt=max_yards)

        total_putts = putts.count()

        if total_putts == 0:
            return 0.0

        made_putts = 0
        for putt in putts.select_related("hole"):
            max_shot_number = putt.hole.shot_set.aggregate(Max("number"))["number__max"]
            if putt.number == max_shot_number:
                made_putts += 1

        return (made_putts / total_putts) * 100

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

    def make_rate_overall(self, user) -> float:
        return self._get_make_rate_for_distance(user, 0, None)

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
            make_rate_overall=self.make_rate_overall(user),
        )
