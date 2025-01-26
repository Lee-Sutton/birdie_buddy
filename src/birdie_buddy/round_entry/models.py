from typing import Self
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from birdie_buddy.round_entry.services import avg_strokes_to_holeout

APPROACH_SHOT_START_DISTANCE = 30

User = get_user_model()


class Round(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=256)
    holes_played = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(18)]
    )


class Hole(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    score = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    mental_scorecard = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    number = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(18)]
    )

    par = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(6)])

    @property
    def strokes_gained(self):
        first_shot = self.shot_set.first()
        return first_shot.avg_strokes_to_holeout - self.score

    @property
    def strokes_gained_driving(self):
        if self.par < 4:
            return 0
        shots = self.shot_set.all()
        if shots.count() == 1:
            return shots[0].strokes_gained(None)
        return shots[0].strokes_gained(shots[1])

    @property
    def strokes_gained_approach(self):
        return self._calculate_strokes_gained(lambda s: s.is_approach_shot)

    @property
    def strokes_gained_putting(self):
        return self._calculate_strokes_gained(lambda s: s.is_putt)

    @property
    def strokes_gained_around_the_green(self):
        return self._calculate_strokes_gained(lambda s: s.is_short_game_shot)

    def _calculate_strokes_gained(self, conditional):
        result = 0
        shots = list(self.shot_set.all())

        for i, shot in enumerate(shots):
            if conditional(shot):
                next_shot = shots[i + 1] if i + 1 < len(shots) else None
                result = result + shot.strokes_gained(next_shot)

        return result

    def __str__(self):
        return str([shot.start_distance for shot in self.shot_set.all()])


class Shot(models.Model):
    # TODO: refactor to an enum
    LIE_CHOICES = [
        ("tee", "Tee"),
        ("fairway", "Fairway"),
        ("rough", "Rough"),
        ("recovery", "Recovery"),
        ("penalty", "Penalty"),
        ("sand", "Sand"),
        ("green", "Green"),
    ]

    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    start_distance = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    lie = models.CharField(max_length=20, choices=LIE_CHOICES, null=True)

    @property
    def avg_strokes_to_holeout(self):
        return avg_strokes_to_holeout(self.start_distance, self.lie)

    def strokes_gained(self, next_shot: Self | None):
        if next_shot is None:
            return self.avg_strokes_to_holeout - 1
        return self.avg_strokes_to_holeout - next_shot.avg_strokes_to_holeout - 1

    @property
    def is_approach_shot(self):
        approach_lies = ["fairway", "rough", "sand"]
        return (
            self.start_distance > APPROACH_SHOT_START_DISTANCE
            and self.lie in approach_lies
        )

    @property
    def is_short_game_shot(self):
        short_game_lies = ["fairway", "rough", "sand"]
        return (
            self.start_distance <= APPROACH_SHOT_START_DISTANCE
            and self.lie in short_game_lies
        )

    @property
    def is_putt(self):
        return self.lie == "green"
