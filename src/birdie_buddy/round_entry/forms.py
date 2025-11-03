from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Field, Div, Submit, Button
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
