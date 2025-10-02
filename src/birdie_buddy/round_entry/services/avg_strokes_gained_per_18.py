from django.db.models import Sum
from birdie_buddy.round_entry.models import Hole
from collections import namedtuple

StrokesGainedCategories = namedtuple(
    "StrokesGainedCategories", ["driving", "approach", "short_game", "putting"]
)


def get_avg_strokes_gained_categories_per_18(user):
    holes = Hole.objects.filter(user=user, score__isnull=False)
    total_holes = holes.count()
    if total_holes == 0:
        return StrokesGainedCategories(0, 0, 0, 0)

    agg = holes.aggregate(
        driving=Sum("strokes_gained_driving"),
        approach=Sum("strokes_gained_approach"),
        short_game=Sum("strokes_gained_around_the_green"),
        putting=Sum("strokes_gained_putting"),
    )

    return StrokesGainedCategories(
        (agg["driving"] or 0) / total_holes * 18,
        (agg["approach"] or 0) / total_holes * 18,
        (agg["short_game"] or 0) / total_holes * 18,
        (agg["putting"] or 0) / total_holes * 18,
    )
