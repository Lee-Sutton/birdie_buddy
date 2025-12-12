import logging
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction

from birdie_buddy.round_entry.models import Round, Hole, Shot, ScorecardUpload
from birdie_buddy.round_entry.services.scorecard_parser_service import ScorecardData
from birdie_buddy.round_entry.services.shot_service import ShotService

User = get_user_model()
logger = logging.getLogger(__name__)


class ScorecardImportService:
    """Service for creating Round/Hole/Shot objects from parsed scorecard data."""

    @staticmethod
    @transaction.atomic
    def create_round_from_scorecard_data(
        user, scorecard_upload: ScorecardUpload, scorecard_data: ScorecardData
    ) -> Optional[Round]:
        """
        Create a Round with all associated Holes and Shots from parsed scorecard data.

        Args:
            user: The user who owns this round
            scorecard_upload: The ScorecardUpload instance to link to
            scorecard_data: Parsed scorecard data containing holes and shots

        Returns:
            The created Round object, or None if creation fails
        """
        try:
            # Create the Round (use course_name from scorecard_upload, not parsed data)
            round_obj = Round.objects.create(
                user=user,
                course_name=scorecard_upload.course_name,
                holes_played=scorecard_data.holes_played,
            )

            # Create all holes and their shots
            for hole_data in scorecard_data.holes:
                hole = Hole.objects.create(
                    user=user,
                    round=round_obj,
                    number=hole_data.number,
                    par=hole_data.par,
                    score=hole_data.score,
                )

                # Create shots for this hole (unsaved)
                shots_to_create = []
                for shot_data in hole_data.shots:
                    shot = Shot(
                        user=user,
                        hole=hole,
                        start_distance=shot_data.start_distance,
                        lie=shot_data.lie,
                    )
                    shots_to_create.append(shot)

                # Use ShotService to calculate strokes gained and save
                ShotService.save_shots_with_strokes_gained(shots_to_create)

            # Link the scorecard upload to the round
            scorecard_upload.round = round_obj
            scorecard_upload.save()

            logger.info(
                f"Successfully created round {round_obj.id} from scorecard upload {scorecard_upload.id}"
            )
            return round_obj

        except Exception as e:
            logger.error(f"Failed to create round from scorecard data: {str(e)}")
            # Transaction will be rolled back automatically
            return None
