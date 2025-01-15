from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from birdie_buddy.round_entry.services import avg_strokes_to_holeout

User = get_user_model()


class Round(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=256)
    holes_played = models.IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(18)]
    )

    def strokes_gained_driving(self):
        pass


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
            return shots[0].avg_strokes_to_holeout
        return shots[0].avg_strokes_to_holeout - shots[1].avg_strokes_to_holeout

    def __str__(self):
        return str([shot.start_distance for shot in self.shot_set.all()])


class Shot(models.Model):
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
