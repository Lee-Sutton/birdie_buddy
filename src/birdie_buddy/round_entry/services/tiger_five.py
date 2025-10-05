from collections import namedtuple
from django.db.models import Count, F
from birdie_buddy.round_entry.models import Shot, Hole

TigerFive = namedtuple(
    "TigerFive",
    ["penalties", "double_bogeys", "three_putts", "bogeys_inside_150", "two_chip"],
)


class TigerFiveService:
    def get_for_user(self, user):
        """Return Tiger Five statistics averaged per 18 holes for `user`.

        Uses smaller helper methods for each stat to keep logic separated.
        """
        total_holes = self._total_holes_with_shots(user)

        if total_holes == 0:
            return TigerFive(0, 0, 0, 0, 0)

        penalties = self.penalties(user)
        double_bogeys = self.double_bogeys(user)
        three_putts = self.three_putts(user)
        bogeys_inside_150 = self.bogeys_inside_150(user)
        two_chip = self.two_chips(user)

        scale = 18 / total_holes

        return TigerFive(
            penalties * scale,
            double_bogeys * scale,
            three_putts * scale,
            bogeys_inside_150 * scale,
            two_chip * scale,
        )

    def penalties(self, user):
        """Count distinct holes with at least one penalty shot."""
        return (
            Shot.objects.filter(user=user, lie="penalty")
            .values("hole")
            .distinct()
            .count()
        )

    def double_bogeys(self, user):
        """Count holes where score >= par + 2."""
        return (
            Hole.objects.filter(user=user)
            .filter(score__isnull=False)
            .filter(score__gte=F("par") + 2)
            .distinct()
            .count()
        )

    def three_putts(self, user):
        """Count holes with 3 or more putts (lie == 'green')."""
        return (
            Shot.objects.filter(user=user, lie="green")
            .values("hole")
            .annotate(putt_count=Count("id"))
            .filter(putt_count__gte=3)
            .count()
        )

    def bogeys_inside_150(self, user):
        """Count bogeys (score == par + 1) where an approach/short-game
        shot started inside 150 yards. Exclude holes with penalty shots.
        """
        return (
            Hole.objects.filter(user=user)
            .filter(score__isnull=False)
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

    def two_chips(self, user):
        """Count holes with exactly two short-game (around_green) shots."""
        return (
            Shot.objects.filter(user=user, shot_type="around_green")
            .values("hole")
            .annotate(chip_count=Count("id"))
            .filter(chip_count=2)
            .count()
        )

    def _total_holes_with_shots(self, user):
        return Shot.objects.filter(user=user).values("hole").distinct().count()
