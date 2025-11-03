from collections import namedtuple
from django.db.models import Count, F
from birdie_buddy.round_entry.models import Shot, Hole

TigerFive = namedtuple(
    "TigerFive",
    ["penalties", "double_bogeys", "three_putts", "bogeys_inside_150", "two_chip"],
)


class TigerFiveService:
    def get_for_user(self, user, round=None):
        """Return Tiger Five statistics averaged per 18 holes for `user`.

        Uses smaller helper methods for each stat to keep logic separated.
        """
        total_holes = self._total_holes_with_shots(user, round)

        if total_holes == 0:
            return TigerFive(0, 0, 0, 0, 0)

        penalties = self.penalties(user, round)
        double_bogeys = self.double_bogeys(user, round)
        three_putts = self.three_putts(user, round)
        bogeys_inside_150 = self.bogeys_inside_150(user, round)
        two_chip = self.two_chips(user, round)

        scale = 18 / total_holes

        return TigerFive(
            penalties * scale,
            double_bogeys * scale,
            three_putts * scale,
            bogeys_inside_150 * scale,
            two_chip * scale,
        )

    def get_for_round(self, round):
        """Return Tiger Five statistics for a specific round (not scaled)."""
        penalties = self.penalties(round.user, round)
        double_bogeys = self.double_bogeys(round.user, round)
        three_putts = self.three_putts(round.user, round)
        bogeys_inside_150 = self.bogeys_inside_150(round.user, round)
        two_chip = self.two_chips(round.user, round)

        return TigerFive(
            penalties,
            double_bogeys,
            three_putts,
            bogeys_inside_150,
            two_chip,
        )

    def penalties(self, user, round=None):
        """Count distinct holes with at least one penalty shot."""
        queryset = Shot.objects.filter(user=user, lie="penalty")
        if round:
            queryset = queryset.filter(hole__round=round)
        return queryset.values("hole").distinct().count()

    def double_bogeys(self, user, round=None):
        """Count holes where score >= par + 2."""
        queryset = Hole.objects.filter(user=user)
        if round:
            queryset = queryset.filter(round=round)
        return (
            queryset.filter(score__isnull=False)
            .filter(score__gte=F("par") + 2)
            .distinct()
            .count()
        )

    def three_putts(self, user, round=None):
        """Count holes with 3 or more putts (lie == 'green')."""
        queryset = Shot.objects.filter(user=user, lie="green")
        if round:
            queryset = queryset.filter(hole__round=round)
        return (
            queryset.values("hole")
            .annotate(putt_count=Count("id"))
            .filter(putt_count__gte=3)
            .count()
        )

    def bogeys_inside_150(self, user, round=None):
        """Count bogeys (score == par + 1) where an approach/short-game
        shot started inside 150 yards. Exclude holes with penalty shots.
        """
        queryset = Hole.objects.filter(user=user)
        if round:
            queryset = queryset.filter(round=round)
        return (
            queryset.filter(score__isnull=False)
            .filter(score=F("par") + 1)
            .filter(
                shot__start_distance__lte=150,
                shot__lie="fairway",
                shot__shot_type__in=["approach", "around_green"],
            )
            .exclude(shot__lie="penalty")
            .distinct()
            .count()
        )

    def two_chips(self, user, round=None):
        """Count holes with exactly two short-game (around_green) shots."""
        queryset = Shot.objects.filter(user=user, shot_type="around_green")
        if round:
            queryset = queryset.filter(hole__round=round)
        return (
            queryset.values("hole")
            .annotate(chip_count=Count("id"))
            .filter(chip_count=2)
            .count()
        )

    def _total_holes_with_shots(self, user, round=None):
        queryset = Shot.objects.filter(user=user)
        if round:
            queryset = queryset.filter(hole__round=round)
        return queryset.values("hole").distinct().count()
