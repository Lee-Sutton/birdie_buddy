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
        shots_created = []
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    shot = form.save(commit=False)
                    shot.hole = hole
                    shot.user = user
                    shot.save()
                    shots_created.append(shot)
        return shots_created

