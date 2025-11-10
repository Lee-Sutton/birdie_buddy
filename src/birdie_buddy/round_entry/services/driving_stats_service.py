"""
Services for driving stats.
"""

from typing import NamedTuple


from birdie_buddy.round_entry.models import Hole, Shot


class DrivingStats(NamedTuple):
    """
    A named tuple to hold driving stats.
    """

    penalties_per_18: float
    rough_per_18: float
    fairways_per_18: float


class RoundDrivingStats(NamedTuple):
    """
    A named tuple to hold driving stats for a specific round.
    """

    penalties: float
    rough: float
    fairways: float


class DrivingStatsService:
    """
    A service to calculate driving stats for a user.
    """

    # 14 drives are 18 per 18 holes on average
    DRIVES_PER_18 = 14

    def _get_tee_shots(self, user):
        """
        Returns a queryset of tee shots for a user on par 4s and 5s.
        """
        return Shot.objects.filter(
            user=user,
        )

    def _drive_ending_lie(self, user, lie: str, round=None) -> float:
        """
        Calculates the number of drives that end up in a specific lie.
        When round is None, normalizes to per-18-hole average.
        When round is provided, returns raw count for that round.
        Only considers par 4 and par 5 holes where the second shot has the given lie.
        """
        filters = {"user": user, "par__in": [4, 5], "shot__number": 2, "shot__lie": lie}
        if round is not None:
            filters["round"] = round

        lie_holes = Hole.objects.filter(**filters).distinct().count()

        if round is not None:
            return lie_holes

        total_filters = {"user": user, "par__in": [4, 5]}
        total_driving_holes = Hole.objects.filter(**total_filters).count()

        if total_driving_holes == 0:
            return 0.0

        return (lie_holes / total_driving_holes) * self.DRIVES_PER_18

    def penalties(self, user, round=None) -> float:
        """
        Calculates the number of tee shots that result in penalties.
        When round is None, returns per-18-hole average.
        When round is provided, returns raw count for that round.
        """
        return self._drive_ending_lie(user, "penalty", round)

    def penalties_per_18(self, user) -> float:
        """
        Calculates the number of tee shots that result in penalties per 18 holes.
        """
        return self.penalties(user, round=None)

    def rough(self, user, round=None) -> float:
        """
        Calculates the number of tee shots that end up in the rough.
        When round is None, returns per-18-hole average.
        When round is provided, returns raw count for that round.
        """
        return self._drive_ending_lie(user, "rough", round)

    def rough_per_18(self, user) -> float:
        """
        Calculates the number of tee shots that end up in the rough per 18 holes.
        """
        return self.rough(user, round=None)

    def fairways(self, user, round=None) -> float:
        """
        Calculates the number of tee shots that end up in the fairway.
        When round is None, returns per-18-hole average.
        When round is provided, returns raw count for that round.
        """
        return self._drive_ending_lie(user, "fairway", round)

    def fairways_per_18(self, user) -> float:
        """
        Calculates the number of tee shots that end up in the fairway per 18 holes.
        """
        return self.fairways(user, round=None)

    def get_for_user(self, user) -> DrivingStats:
        """
        Returns all driving statistics for a user.
        """
        return DrivingStats(
            penalties_per_18=self.penalties(user),
            rough_per_18=self.rough(user),
            fairways_per_18=self.fairways(user),
        )

    def get_for_round(self, round) -> RoundDrivingStats:
        """
        Returns all driving statistics for a round.
        """
        return RoundDrivingStats(
            penalties=self.penalties(round.user, round),
            rough=self.rough(round.user, round),
            fairways=self.fairways(round.user, round),
        )
