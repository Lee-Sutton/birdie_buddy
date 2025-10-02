from typing import Self
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from birdie_buddy.round_entry.services import avg_strokes_to_holeout

APPROACH_SHOT_START_DISTANCE = 30
TEE_SHOT_START_DISTANCE = 250

User = get_user_model()


class Round(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=256)
    holes_played = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(18)]
    )

    @property
    def strokes_gained_driving(self):
        return sum([hole.strokes_gained_driving for hole in self.hole_set.all()])

    @property
    def strokes_gained_approach(self):
        return sum([hole.strokes_gained_approach for hole in self.hole_set.all()])

    @property
    def strokes_gained_putting(self):
        return sum([hole.strokes_gained_putting for hole in self.hole_set.all()])

    @property
    def strokes_gained_around_the_green(self):
        return sum(
            [hole.strokes_gained_around_the_green for hole in self.hole_set.all()]
        )

    @property
    def complete(self):
        holes = self.hole_set.annotate(num_shots=models.Count("shot")).filter(
            num_shots__gte=1
        )
        return holes.count() == self.holes_played


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
            return shots[0].calculate_strokes_gained(None)
        return shots[0].calculate_strokes_gained(shots[1])

    @property
    def strokes_gained_approach(self):
        return self._calculate_strokes_gained(lambda s: s.is_approach_shot)

    @property
    def strokes_gained_putting(self):
        result = 0

        for putt in self.shot_set.filter(shot_type="putt"):
            result = result + putt.strokes_gained

        return result

    @property
    def strokes_gained_around_the_green(self):
        return self._calculate_strokes_gained(lambda s: s.is_short_game_shot)

    def _calculate_strokes_gained(self, conditional):
        result = 0
        shots = list(self.shot_set.all())

        for i, shot in enumerate(shots):
            if conditional(shot):
                next_shot = shots[i + 1] if i + 1 < len(shots) else None
                result = result + shot.calculate_strokes_gained(next_shot)

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

    SHOT_TYPE_CHOICES = [
        ("drive", "Drive"),
        ("approach", "Approach"),
        ("around_green", "Around the Green"),
        ("putt", "Putt"),
    ]

    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    start_distance = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    lie = models.CharField(max_length=20, choices=LIE_CHOICES, null=True)
    strokes_gained = models.FloatField(null=True)
    shot_type = models.CharField(max_length=16, choices=SHOT_TYPE_CHOICES, null=True)

    def save(self, *args, **kwargs):
        if self.is_putt:
            self.shot_type = "putt"
        elif self.is_short_game_shot:
            self.shot_type = "around_green"
        elif self.is_approach_shot:
            self.shot_type = "approach"
        elif self.is_tee_shot:
            self.shot_type = "drive"
        else:
            self.shot_type = None
        super().save(*args, **kwargs)

    @property
    def avg_strokes_to_holeout(self):
        return avg_strokes_to_holeout(self.start_distance, self.lie)

    def calculate_strokes_gained(self, next_shot: Self | None):
        if next_shot is None:
            self.strokes_gained = self.avg_strokes_to_holeout - 1
        else:
            self.strokes_gained = (
                self.avg_strokes_to_holeout - next_shot.avg_strokes_to_holeout - 1
            )
        return self.strokes_gained

    def get_next_shot(self):
        shots = list(self.hole.shot_set.order_by("id"))
        try:
            idx = shots.index(self)
            return shots[idx + 1] if idx + 1 < len(shots) else None
        except ValueError:
            return None

    @property
    def is_tee_shot(self):
        return self.lie == "tee" and not self.is_approach_shot

    @property
    def is_approach_shot(self):
        approach_lies = ["tee", "fairway", "rough", "sand"]
        result = (
            self.start_distance is not None
            and self.start_distance <= TEE_SHOT_START_DISTANCE
            and self.start_distance > APPROACH_SHOT_START_DISTANCE
            and self.lie in approach_lies
        )
        return result

    @property
    def is_short_game_shot(self):
        short_game_lies = ["fairway", "rough", "sand"]
        return (
            self.start_distance is not None
            and self.start_distance <= APPROACH_SHOT_START_DISTANCE
            and self.lie in short_game_lies
        )

    @property
    def is_putt(self):
        return self.lie == "green"

    def __str__(self):
        return f"{self.lie} - {self.start_distance} - {self.strokes_gained}"
