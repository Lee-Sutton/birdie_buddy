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
