from django.shortcuts import render

from birdie_buddy.round_entry.services.avg_strokes_gained_per_18 import (
    get_avg_strokes_gained_categories_per_18,
)
from birdie_buddy.round_entry.services.tiger_five import TigerFiveService


def stats_view(req):
    stats = get_avg_strokes_gained_categories_per_18(req.user)
    tiger = TigerFiveService().get_for_user(req.user)
    return render(
        req,
        "stats.html",
        {
            "strokes_gained_driving": stats.driving,
            "strokes_gained_approach": stats.approach,
            "strokes_gained_putting": stats.putting,
            "strokes_gained_around_the_green": stats.short_game,
            "tiger": tiger,
        },
    )
