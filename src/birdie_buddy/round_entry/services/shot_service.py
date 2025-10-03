from birdie_buddy.round_entry.models import Shot, Hole
from django.contrib.auth.models import User
from django.forms import BaseFormSet


class ShotService:
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

        for i, shot in enumerate(shots_created):
            next_shot = shots_created[i + 1] if i + 1 < len(shots_created) else None
            shot.calculate_strokes_gained(next_shot)
            shot.save()

        # TODO: we may want to mark the round as complete here as well

        return shots_created
