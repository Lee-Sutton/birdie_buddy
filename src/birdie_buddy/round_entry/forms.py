from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from birdie_buddy.round_entry.models import Shot


class ShotForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = ["start_distance", "lie"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "space-y-4"  # Tailwind spacing between form elements
        self.helper.layout = Layout(
            Row(
                Column(
                    "start_distance", css_class="w-1/2 px-2"
                ),  # Tailwind utility classes
                Column("lie", css_class="w-1/2 px-2"),
                css_class="flex space-x-4",  # Add spacing between columns
            )
        )
