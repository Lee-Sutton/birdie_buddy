import base64
import logging
from typing import Optional

import requests
from django.conf import settings
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class ScorecardParserService:
    """Service for parsing scorecard images using Google Cloud Vision REST API"""

    def __init__(self):
        self.api_key = settings.GCLOUD_VISION_API_KEY
        self.api_url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"

    def parse_scorecard_image(self, image_field) -> Optional[dict]:
        """
        Extract text and bounding box data from a scorecard image using Google Cloud Vision

        Args:
            image_field: Django ImageField instance (e.g., scorecard_upload.scorecard_image)

        Returns:
            Dictionary containing 'text' and 'full_response' keys, or None if extraction fails
        """
        try:
            # Read file from storage (works with Azure Blob Storage)
            with default_storage.open(image_field.name, "rb") as image_file:
                content = image_file.read()

            # Encode image to base64
            image_base64 = base64.b64encode(content).decode("utf-8")

            # Prepare API request
            request_body = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                    }
                ]
            }

            response = requests.post(self.api_url, json=request_body)
            response.raise_for_status()

            result = response.json()

            # Log full response for inspection
            logger.info(f"Full Google Vision API response:\n{result}")

            if "responses" in result and len(result["responses"]) > 0:
                response_data = result["responses"][0]

                if "error" in response_data:
                    logger.error(f"Google Vision API error: {response_data['error']}")
                    return None

                if "fullTextAnnotation" in response_data:
                    # Log full text annotation structure
                    logger.info(f"Full text annotation:\n{response_data['fullTextAnnotation']}")
                    print(response_data["fullTextAnnotation"]["text"])
                    return {
                        "text": response_data["fullTextAnnotation"]["text"],
                        "full_response": response_data
                    }

            return None

        except FileNotFoundError:
            logger.error(f"Image file not found: {image_field.name}")
            return None
        except requests.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing scorecard image: {str(e)}")
            return None
