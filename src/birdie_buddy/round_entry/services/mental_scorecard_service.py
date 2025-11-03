from dataclasses import dataclass
from django.db.models import Avg

from birdie_buddy.round_entry.models import Hole, Round


@dataclass
class MentalScorecardStats:
    avg_mental_scorecard_per_18: float
    avg_actual_score_per_18: float
    mental_vs_actual_pct: float
    rounds_with_mental_data: int


class MentalScorecardService:
    def get_for_user(self, user) -> MentalScorecardStats:
        holes_with_mental = Hole.objects.filter(
            user=user, mental_scorecard__isnull=False, score__isnull=False
        )

        if not holes_with_mental.exists():
            return MentalScorecardStats(
                avg_mental_scorecard_per_18=0.0,
                avg_actual_score_per_18=0.0,
                mental_vs_actual_pct=0.0,
                rounds_with_mental_data=0,
            )

        stats = holes_with_mental.aggregate(
            avg_mental=Avg("mental_scorecard"), avg_score=Avg("score")
        )

        avg_mental_per_hole = stats["avg_mental"] or 0.0
        avg_score_per_hole = stats["avg_score"] or 0.0

        avg_mental_per_18 = avg_mental_per_hole * 18
        avg_score_per_18 = avg_score_per_hole * 18

        if avg_score_per_18 > 0:
            mental_vs_actual_pct = (avg_mental_per_18 / avg_score_per_18) * 100
        else:
            mental_vs_actual_pct = 0.0

        rounds_with_mental = (
            Round.objects.filter(user=user, hole__mental_scorecard__isnull=False)
            .distinct()
            .count()
        )

        return MentalScorecardStats(
            avg_mental_scorecard_per_18=avg_mental_per_18,
            avg_actual_score_per_18=avg_score_per_18,
            mental_vs_actual_pct=mental_vs_actual_pct,
            rounds_with_mental_data=rounds_with_mental,
        )
