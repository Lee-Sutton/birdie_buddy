from django.db.models import Sum
from birdie_buddy.round_entry.models import Shot
from collections import namedtuple

StrokesGainedCategories = namedtuple(
    "StrokesGainedCategories", ["driving", "approach", "short_game", "putting"]
)


def get_avg_strokes_gained_categories_per_18(user):
    shots = Shot.objects.filter(user=user, strokes_gained__isnull=False)
    total_holes = shots.values("hole").distinct().count()
    if total_holes == 0:
        return StrokesGainedCategories(0, 0, 0, 0)

    driving = (
        shots.filter(shot_type="drive").aggregate(Sum("strokes_gained"))[
            "strokes_gained__sum"
        ]
        or 0
    )
    approach = (
        shots.filter(shot_type="approach").aggregate(Sum("strokes_gained"))[
            "strokes_gained__sum"
        ]
        or 0
    )
    short_game = (
        shots.filter(shot_type="around_green").aggregate(Sum("strokes_gained"))[
            "strokes_gained__sum"
        ]
        or 0
    )
    putting = (
        shots.filter(shot_type="putt").aggregate(Sum("strokes_gained"))[
            "strokes_gained__sum"
        ]
        or 0
    )

    return StrokesGainedCategories(
        driving / total_holes * 18,
        approach / total_holes * 18,
        short_game / total_holes * 18,
        putting / total_holes * 18,
    )
