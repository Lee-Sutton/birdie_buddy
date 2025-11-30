from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Field, Div
from django import forms

from birdie_buddy.round_entry.models import Shot


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
            {"class": "sr-only", "id": "file-upload"}
        )
