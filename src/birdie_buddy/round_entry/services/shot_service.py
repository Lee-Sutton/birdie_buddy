from birdie_buddy.round_entry.models import Shot, Hole
from django.contrib.auth.models import User
from django.forms import BaseFormSet


class ShotService:
    @staticmethod
    def save_shots_with_strokes_gained(shots: list[Shot]) -> list[Shot]:
        """
        Calculate strokes gained for each shot and save them to the database.

        This method handles the core logic of calculating strokes gained based on
        the next shot in the sequence, then saves all shots.

        Args:
            shots: List of Shot objects (not yet saved to DB) in order

        Returns:
            List of saved Shot objects with strokes gained calculated
        """
        for i, shot in enumerate(shots):
            next_shot = shots[i + 1] if i + 1 < len(shots) else None
            shot.number = i + 1
            shot.calculate_strokes_gained(next_shot)
            shot.save()

        return shots

    @staticmethod
    def create_shots_for_hole(hole: Hole, user: User, formset: BaseFormSet):
        """
        Deletes existing shots for the given hole and user,
        then creates new shots based on the provided formset data.
        """
        # Delete existing shots for the current hole
        Shot.objects.filter(hole=hole, user=user).delete()

        # Create new shots
        shots_created: list[Shot] = []
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    shot: Shot = form.save(commit=False)
                    shot.hole = hole
                    shot.user = user
                    shots_created.append(shot)

        # Use the shared method to calculate strokes gained and save
        ShotService.save_shots_with_strokes_gained(shots_created)

        # TODO: we may want to mark the round as complete here as well

        return shots_created
