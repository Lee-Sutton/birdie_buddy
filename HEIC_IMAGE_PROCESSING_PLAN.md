# HEIC Image Processing Implementation Plan

## Overview
Add support for HEIC image uploads and ensure all images are optimized to stay under Claude API's 5MB limit.

## Requirements Summary
1. Support HEIC image uploads (auto-convert to JPEG)
2. Ensure all images stay under 5MB for Claude API compatibility
3. Automatic compression/resizing with balanced quality (80%)
4. Store only the processed version to save storage costs
5. Update UI to reflect HEIC support

## Implementation Steps

### 1. Add pillow-heif dependency

**File: `pyproject.toml`**

```toml
dependencies = [
    # ... existing dependencies ...
    "pillow>=12.0.0",
    "pillow-heif>=0.15.0",  # ADD THIS LINE
    "django-storages[azure]>=1.14.6",
    # ... rest of dependencies ...
]
```

**Command to run:**
```bash
rye sync
```

---

### 2. Create Image Processing Service

**File: `src/birdie_buddy/round_entry/services/image_processing_service.py`** (NEW FILE)

```python
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
    """Service for processing scorecard images before sending to Claude API."""

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
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for images with transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize if needed (maintain aspect ratio)
            if max(image.size) > ImageProcessingService.MAX_DIMENSION:
                image.thumbnail(
                    (ImageProcessingService.MAX_DIMENSION, ImageProcessingService.MAX_DIMENSION),
                    Image.Resampling.LANCZOS
                )
                logger.info(f"Resized image to {image.size}")

            # Compress to stay under 5MB
            quality = ImageProcessingService.INITIAL_QUALITY
            output = io.BytesIO()

            while quality >= ImageProcessingService.MIN_QUALITY:
                output.seek(0)
                output.truncate()

                image.save(output, format='JPEG', quality=quality, optimize=True)
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
                logger.warning("Could not compress to 5MB, attempting more aggressive resize")
                scale_factor = 0.8
                new_size = (int(image.size[0] * scale_factor), int(image.size[1] * scale_factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

                output.seek(0)
                output.truncate()
                image.save(output, format='JPEG', quality=ImageProcessingService.MIN_QUALITY, optimize=True)
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
                field_name='scorecard_image',
                name=ImageProcessingService._get_output_filename(uploaded_file.name),
                content_type='image/jpeg',
                size=output.tell(),
                charset=None
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
```

---

### 3. Update ScorecardUploadForm

**File: `src/birdie_buddy/round_entry/forms.py`**

```python
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Field, Div
from django import forms
from django.core.exceptions import ValidationError

from birdie_buddy.round_entry.models import Shot
from birdie_buddy.round_entry.services.image_processing_service import ImageProcessingService


class ShotForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = ["start_distance", "lie"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_distance"].widget.attrs["autofocus"] = True


class ShotFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_pack = "tailwind"
        self.form_tag = False  # Disable form tags for individual forms
        self.layout = Layout(
            Div(
                Div(
                    Field("start_distance"),
                    css_class="w-full",
                ),
                Div(Field("lie"), css_class="w-full"),
                css_class="flex space-x-4",
            )
        )


class ScorecardUploadForm(forms.Form):
    course_name = forms.CharField(required=True)
    scorecard_image = forms.ImageField(widget=forms.FileInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course_name"].widget.attrs.update(
            {
                "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            }
        )
        self.fields["scorecard_image"].widget.attrs.update(
            {"class": "sr-only", "id": "file-upload", "accept": "image/jpeg,image/jpg,image/png,image/gif,image/heic,image/heif"}
        )

    def clean_scorecard_image(self):
        """Process the uploaded image to ensure compatibility with Claude API."""
        uploaded_file = self.cleaned_data.get('scorecard_image')

        if not uploaded_file:
            return uploaded_file

        # Process the image (convert HEIC, resize, compress)
        processed_file = ImageProcessingService.process_image(uploaded_file)

        if processed_file is None:
            raise ValidationError(
                "Unable to process the uploaded image. Please try a different image or "
                "ensure the file is a valid image format (JPG, PNG, GIF, or HEIC)."
            )

        return processed_file
```

**Key changes:**
- Import `ImageProcessingService` and `ValidationError`
- Add `accept` attribute to file input to allow HEIC files
- Add `clean_scorecard_image()` method to process images on upload
- Replace uploaded file with processed version

---

### 4. Update UI Text

**File: `src/birdie_buddy/round_entry/templates/round_entry/scorecard_image_field.html`**

Find line ~57 and change:
```html
<!-- OLD -->
<p class="text-xs/5 text-gray-600">PNG, JPG, GIF up to 10MB</p>

<!-- NEW -->
<p class="text-xs/5 text-gray-600">PNG, JPG, GIF, HEIC supported - automatically optimized for processing</p>
```

---

## Testing Plan

### 1. Test HEIC File Upload
1. Take a photo with iPhone (saves as HEIC by default)
2. Upload to scorecard form
3. Verify it's converted to JPEG
4. Verify it's processed by Claude successfully

### 2. Test Large Image (>5MB)
1. Find or create a high-resolution image >5MB
2. Upload to scorecard form
3. Verify it's compressed to <5MB
4. Check image quality is still readable
5. Verify Claude can parse it

### 3. Test Edge Cases
- Very small images (<200px)
- Very large images (8000px+)
- Images with transparency (PNG with alpha channel)
- Corrupted/invalid image files

### 4. Manual Testing Commands

```bash
# Run Django checks
python manage.py check

# Run existing tests to ensure nothing broke
rye run pytest src/birdie_buddy/round_entry/models_test.py -q

# Start dev server and test manually
python manage.py runserver
```

---

## Rollback Plan

If issues occur:

1. **Revert pyproject.toml** - Remove `pillow-heif>=0.15.0`
2. **Delete image_processing_service.py**
3. **Revert forms.py** - Remove `clean_scorecard_image()` method and accept attribute
4. **Revert UI text** - Change back to original message
5. Run `rye sync` to remove pillow-heif

---

## Notes

- **Storage savings**: By storing only processed versions, we save significant storage costs (especially for HEIC files which can be large)
- **User experience**: Processing happens during upload, so users get immediate feedback if there's an issue
- **Quality**: 80% JPEG quality provides good balance between file size and readability
- **Compatibility**: All major image formats supported (JPEG, PNG, GIF, HEIC/HEIF)
- **API compliance**: Ensures all images meet Claude API requirements (5MB, max 1568px)

---

## Implementation Checklist

- [x] Add pillow-heif to pyproject.toml (DONE - already added)
- [ ] Run `rye sync` to install dependency
- [ ] Create `image_processing_service.py`
- [ ] Update `forms.py` with image processing
- [ ] Update UI text in `scorecard_image_field.html`
- [ ] Run Django checks
- [ ] Test with HEIC file
- [ ] Test with large image
- [ ] Test with normal images (regression test)
- [ ] Verify Claude API still works
- [ ] Commit changes

---

## Git Commit Message (when ready)

```
feat: add HEIC support and automatic image optimization

- Add pillow-heif for HEIC/HEIF image support
- Auto-convert HEIC to JPEG on upload
- Resize images to max 1568px (Anthropic recommendation)
- Compress images to stay under 5MB Claude API limit
- Use balanced quality (80%) for good size/quality tradeoff
- Store only processed version to save storage costs
- Update UI to reflect HEIC support

Fixes issue where users couldn't upload iPhone photos (HEIC format)
and large images would fail Claude API processing.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
