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
