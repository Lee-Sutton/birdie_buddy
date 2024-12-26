from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

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
