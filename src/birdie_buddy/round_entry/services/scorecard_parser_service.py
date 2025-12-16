import base64
import json
import logging
from dataclasses import dataclass
from typing import Optional

import anthropic
from django.conf import settings
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


@dataclass
class ShotData:
    """Data class representing a single shot parsed from a scorecard."""

    number: int
    start_distance: int
    lie: str  # tee, fairway, rough, recovery, penalty, sand, green


@dataclass
class HoleData:
    """Data class representing a single hole parsed from a scorecard."""

    number: int
    par: int
    score: int
    shots: list[ShotData]


@dataclass
class ScorecardData:
    """Data class representing parsed scorecard data."""

    holes: list[HoleData]

    @property
    def holes_played(self) -> int:
        return len(self.holes)


class ScorecardParserService:
    """Service for parsing scorecard images using Anthropic's Claude multimodal LLM."""

    VALID_LIES = ["tee", "fairway", "rough", "recovery", "penalty", "sand", "green"]

    def __init__(self, client: Optional[anthropic.Anthropic] = None):
        self.api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
        self.client = client or anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

    def parse_scorecard_image(self, image_field) -> tuple[Optional[ScorecardData], Optional[dict]]:
        """
        Parse a scorecard image using Anthropic's Claude multimodal LLM.

        Args:
            image_field: Django ImageField instance (e.g., scorecard_upload.scorecard_image)

        Returns:
            Tuple of (ScorecardData object, raw JSON dict) or (None, None) if parsing fails
        """
        if not self.api_key:
            logger.warning("Anthropic API key not configured")
            return None, None

        try:
            # Read and encode the image
            image_base64 = self._encode_image(image_field)
            if not image_base64:
                return None, None

            # Get the media type
            media_type = self._get_media_type(image_field.name)

            # Call the LLM
            response = self._call_llm(image_base64, media_type)
            print(response)
            if not response:
                return None, None

            # Parse the response into structured data
            return self._parse_response(response)

        except Exception as e:
            logger.error(f"Error parsing scorecard image: {str(e)}")
            return None, None

    def _encode_image(self, image_field) -> Optional[str]:
        """Read and base64 encode an image from storage."""
        try:
            with default_storage.open(image_field.name, "rb") as image_file:
                content = image_file.read()
            return base64.b64encode(content).decode("utf-8")
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_field.name}")
            return None
        except Exception as e:
            logger.error(f"Error reading image file: {str(e)}")
            return None

    def _get_media_type(self, filename: str) -> str:
        """Determine the media type from the filename."""
        lower_name = filename.lower()
        if lower_name.endswith(".png"):
            return "image/png"
        elif lower_name.endswith(".gif"):
            return "image/gif"
        elif lower_name.endswith(".webp"):
            return "image/webp"
        else:
            # Default to JPEG for .jpg, .jpeg, or unknown
            return "image/jpeg"

    def _build_system_prompt(self) -> str:
        """Build the system prompt for scorecard parsing."""
        return """You are a golf scorecard parser.

IMPORTANT: The scorecard image may be rotated or oriented in any direction (upside down, sideways, etc.).
Please analyze the image regardless of its orientation and extract the data correctly.

Analyze the scorecard image and extract the following information for each hole played:
1. Hole number (1-18)
2. Par for the hole (3, 4, or 5)
3. Score (total strokes for the hole)
4. Individual shots with:
   - Shot number (1, 2, 3, etc.)
   - Starting distance to the hole (in yards for non-putts, in feet for putts on the green)
   - Lie type: one of "tee", "fairway", "rough", "recovery", "penalty", "sand", "green". This is denoted on the scorecard as: T, F, R, X, P, S, G respectively.

Description of scorecard:
The scorecard is a specialized card for tracking strokes gained. 
It should have the following headers: Hole Number (1 through 18), Par (3, 4, or 5)
The columns are: Stroke, Start Lie, Start distance to the hole

Return the data as a JSON object with this exact structure:
{
    "holes": [
        {
            "number": 1,
            "par": 4,
            "shots": [
                {"number": 1, "start_distance": 380, "lie": "tee"},
                {"number": 2, "start_distance": 150, "lie": "fairway"},
                {"number": 3, "start_distance": 25, "lie": "green"},
                {"number": 4, "start_distance": 8, "lie": "green"},
                {"number": 5, "start_distance": 2, "lie": "green"}
            ]
        }
    ]
}

Important:
- Only include holes that were actually played (have shot data)
- Be consistent with lie types based on the scorecard notation
- Return ONLY the JSON object, no additional text or markdown formatting"""

    def _call_llm(self, image_base64: str, media_type: str) -> Optional[str]:
        """Call Anthropic's Claude multimodal LLM with the scorecard image."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Please parse this golf scorecard image and extract the hole and shot data as JSON.",
                            },
                        ],
                    }
                ],
                system=self._build_system_prompt(),
            )

            # Extract text content from the response
            content = message.content[0].text
            logger.info(f"LLM response: {content}")
            return content

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            return None

    def _parse_response(self, response: str) -> tuple[Optional[ScorecardData], Optional[dict]]:
        """Parse the LLM response into structured ScorecardData and return raw JSON."""
        try:
            # Clean up response if it contains markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)

            holes = []

            for hole_data in data.get("holes", []):
                shots = []
                for shot_data in hole_data.get("shots", []):
                    # Validate lie type
                    lie = shot_data.get("lie", "fairway").lower()
                    if lie not in self.VALID_LIES:
                        lie = "fairway"  # Default fallback

                    shots.append(
                        ShotData(
                            number=shot_data.get("number", 1),
                            start_distance=shot_data.get("start_distance", 0),
                            lie=lie,
                        )
                    )

                holes.append(
                    HoleData(
                        number=hole_data.get("number", 0),
                        par=hole_data.get("par", 4),
                        score=len(shots),  # Calculate score from number of shots
                        shots=shots,
                    )
                )

            scorecard_data = ScorecardData(holes=holes)
            return scorecard_data, data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response was: {response}")
            return None, None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return None, None
