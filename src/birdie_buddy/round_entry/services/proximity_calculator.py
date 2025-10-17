from django.db.models import F, Window
from django.db.models.functions import Lead

from birdie_buddy.round_entry.models import Shot


class ProximityCalculator:
    def calculate_avg_proximity(
        self,
        user,
        shot_type: str,
        min_distance: int,
        max_distance: int | None,
        lie: str | None = None,
    ) -> float:
        shots_with_next = Shot.objects.filter(user=user).annotate(
            next_distance=Window(
                expression=Lead("start_distance"),
                partition_by=[F("hole_id")],
                order_by=F("id").asc(),
            )
        )

        proximities = []
        for shot in shots_with_next:
            if (
                shot.shot_type == shot_type
                and shot.start_distance >= min_distance
                and (max_distance is None or shot.start_distance < max_distance)
                and (lie is None or shot.lie == lie)
                and shot.next_distance is not None
            ):
                proximities.append(shot.next_distance)

        if not proximities:
            return 0.0

        return sum(proximities) / len(proximities)
