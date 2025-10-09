"""
Services for driving stats.
"""

from typing import NamedTuple

from django.db.models import Avg, F, Window
from django.db.models.functions import Lead

from birdie_buddy.round_entry.models import Hole, Shot


class DrivingStats(NamedTuple):
    """
    A named tuple to hold driving stats.
    """

    penalties_per_18: float
    rough_per_18: float


class DrivingStatsService:
    """
    A service to calculate driving stats for a user.
    """

    def _get_tee_shots(self, user):
        """
        Returns a queryset of tee shots for a user on par 4s and 5s.
        """
        return Shot.objects.filter(
            user=user,
        )

    def penalties_per_18(self, user) -> float:
        """
        Calculates the number of tee shots that result in penalties per 18 holes.
        Only considers par 4 and par 5 holes where the second shot is a penalty.
        """
        # Count holes with penalty second shots on par 4/5s
        penalty_holes = (
            Hole.objects.filter(
                user=user, par__in=[4, 5], shot__number=2, shot__lie="penalty"
            )
            .distinct()
            .count()
        )

        # Total par 4/5 holes played
        total_driving_holes = Hole.objects.filter(user=user, par__in=[4, 5]).count()

        if total_driving_holes == 0:
            return 0.0

        # Scale to per 18 holes
        return (penalty_holes / total_driving_holes) * 18

    def rough_per_18(self, user) -> float:
        """
        Calculates the number of tee shots that end up in the rough per 18 holes.
        Only considers par 4 and par 5 holes where the second shot is from the rough.
        """
        # Count holes with rough second shots on par 4/5s
        rough_holes = (
            Hole.objects.filter(
                user=user, par__in=[4, 5], shot__number=2, shot__lie="rough"
            )
            .distinct()
            .count()
        )

        # Total par 4/5 holes played
        total_driving_holes = Hole.objects.filter(user=user, par__in=[4, 5]).count()

        if total_driving_holes == 0:
            return 0.0

        # Scale to per 18 holes
        return (rough_holes / total_driving_holes) * 18

    def get_for_user(self, user) -> DrivingStats:
        """
        Returns all driving statistics for a user.
        """
        return DrivingStats(
            penalties_per_18=self.penalties_per_18(user),
            rough_per_18=self.rough_per_18(user),
        )
