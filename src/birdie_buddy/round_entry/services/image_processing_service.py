import io
import logging
from typing import Optional

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from pillow_heif import register_heif_opener

logger = logging.getLogger(__name__)

# Register HEIF/HEIC support with Pillow
register_heif_opener()


class ImageProcessingService:
    """Service for processing scorecard images before sending to LLM API."""

    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    MAX_DIMENSION = 1568  # Anthropic's recommended max dimension
    INITIAL_QUALITY = 80  # Balanced quality
    MIN_QUALITY = 60  # Don't go below this

    @staticmethod
    def process_image(uploaded_file) -> Optional[InMemoryUploadedFile]:
        """
        Process an uploaded image to ensure it's compatible with Claude API.

        Steps:
        1. Convert HEIC to JPEG if needed
        2. Resize if dimensions exceed MAX_DIMENSION
        3. Compress to stay under MAX_FILE_SIZE_BYTES

        Args:
            uploaded_file: Django UploadedFile instance

        Returns:
            Processed InMemoryUploadedFile ready for Claude API, or None if processing fails
        """
        try:
            # Open the image with Pillow (HEIC support via pillow-heif)
            image = Image.open(uploaded_file)

            # Convert to RGB (required for JPEG, handles HEIC and PNG with transparency)
            if image.mode in ("RGBA", "LA", "P"):
                # Create white background for images with transparency
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(
                    image,
                    mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None,
                )
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            # Resize if needed (maintain aspect ratio)
            if max(image.size) > ImageProcessingService.MAX_DIMENSION:
                image.thumbnail(
                    (
                        ImageProcessingService.MAX_DIMENSION,
                        ImageProcessingService.MAX_DIMENSION,
                    ),
                    Image.Resampling.LANCZOS,
                )
                logger.info(f"Resized image to {image.size}")

            # Compress to stay under 5MB
            quality = ImageProcessingService.INITIAL_QUALITY
            output = io.BytesIO()

            while quality >= ImageProcessingService.MIN_QUALITY:
                output.seek(0)
                output.truncate()

                image.save(output, format="JPEG", quality=quality, optimize=True)
                file_size = output.tell()

                if file_size <= ImageProcessingService.MAX_FILE_SIZE_BYTES:
                    logger.info(
                        f"Compressed image to {file_size / (1024 * 1024):.2f}MB "
                        f"at quality {quality}"
                    )
                    break

                quality -= 5
            else:
                # If we couldn't get under 5MB even at MIN_QUALITY, try more aggressive resize
                logger.warning(
                    "Could not compress to 5MB, attempting more aggressive resize"
                )
                scale_factor = 0.8
                new_size = (
                    int(image.size[0] * scale_factor),
                    int(image.size[1] * scale_factor),
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)

                output.seek(0)
                output.truncate()
                image.save(
                    output,
                    format="JPEG",
                    quality=ImageProcessingService.MIN_QUALITY,
                    optimize=True,
                )
                file_size = output.tell()

                if file_size > ImageProcessingService.MAX_FILE_SIZE_BYTES:
                    logger.error(
                        f"Failed to compress image to under {ImageProcessingService.MAX_FILE_SIZE_MB}MB. "
                        f"Final size: {file_size / (1024 * 1024):.2f}MB"
                    )
                    return None

            # Create new InMemoryUploadedFile
            output.seek(0)
            processed_file = InMemoryUploadedFile(
                file=output,
                field_name="scorecard_image",
                name=ImageProcessingService._get_output_filename(uploaded_file.name),
                content_type="image/jpeg",
                size=output.tell(),
                charset=None,
            )

            return processed_file

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

    @staticmethod
    def _get_output_filename(original_filename: str) -> str:
        """Convert original filename to .jpg extension."""
        import os

        name_without_ext = os.path.splitext(original_filename)[0]
        return f"{name_without_ext}.jpg"
