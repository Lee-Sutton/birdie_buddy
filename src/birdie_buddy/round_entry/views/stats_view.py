from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from birdie_buddy.round_entry.services.avg_strokes_gained_per_18 import (
    get_avg_strokes_gained_categories_per_18,
)
from birdie_buddy.round_entry.services.tiger_five import TigerFiveService
from birdie_buddy.round_entry.services.driving_stats_service import DrivingStatsService
from birdie_buddy.round_entry.services.approach_stats_service import ApproachShotService
from birdie_buddy.round_entry.services.short_game_service import ShortGameService
from birdie_buddy.round_entry.services.putting_stats_service import PuttingStatsService
from birdie_buddy.round_entry.services.mental_scorecard_service import (
    MentalScorecardService,
)


@login_required
def stats_view(req):
    stats = get_avg_strokes_gained_categories_per_18(req.user)
    tiger = TigerFiveService().get_for_user(req.user)
    driving_stats = DrivingStatsService().get_for_user(req.user)
    approach_stats = ApproachShotService().get_for_user(req.user)
    short_game_stats = ShortGameService().get_for_user(req.user)
    putting_stats = PuttingStatsService().get_for_user(req.user)
    mental_stats = MentalScorecardService().get_for_user(req.user)
    return render(
        req,
        "stats.html",
        {
            "strokes_gained_driving": stats.driving,
            "strokes_gained_approach": stats.approach,
            "strokes_gained_putting": stats.putting,
            "strokes_gained_around_the_green": stats.short_game,
            "tiger": tiger,
            "driving_stats": driving_stats,
            "approach_stats": approach_stats,
            "short_game_stats": short_game_stats,
            "putting_stats": putting_stats,
            "mental_stats": mental_stats,
        },
    )
