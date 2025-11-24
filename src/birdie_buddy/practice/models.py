from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PracticeSession(models.Model):
    class PracticeType(models.TextChoices):
        FULL_SWING = "FS", "Full Swing"
        SHORT_GAME = "SG", "Short Game"
        PUTTING = "PT", "Putting"

    class Outcome(models.IntegerChoices):
        POOR = 1, "Poor"
        AVERAGE = 2, "Average"
        GOOD = 3, "Good"
        EXCELLENT = 4, "Excellent"

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    practice_type = models.CharField(
        max_length=2,
        choices=PracticeType.choices,
        default=PracticeType.FULL_SWING,
    )
    outcome = models.IntegerField(
        choices=Outcome.choices,
        default=Outcome.AVERAGE,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
