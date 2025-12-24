from birdie_buddy.round_entry.models import Hole


class HoleService:
    """Service for hole-related business logic."""

    @staticmethod
    def delete_hole(hole: Hole) -> None:
        """
        Delete a hole and handle associated business logic.

        This method:
        1. Deletes the specified hole (shots cascade automatically)
        2. Renumbers all subsequent holes in the round
        3. Decrements the round's holes_played count

        Args:
            hole: The Hole instance to delete
        """
        round_obj = hole.round
        deleted_hole_number = hole.number

        # Delete the hole (shots cascade automatically via ForeignKey)
        hole.delete()

        # Renumber subsequent holes (holes with number > deleted hole)
        subsequent_holes = list(
            Hole.objects.filter(
                round=round_obj,
                number__gt=deleted_hole_number
            ).order_by('number')
        )

        for hole in subsequent_holes:
            hole.number -= 1

        # Bulk update for efficiency (single query instead of N queries)
        if subsequent_holes:
            Hole.objects.bulk_update(subsequent_holes, ['number'])

        # Update holes_played count
        round_obj.holes_played -= 1
        round_obj.save()
