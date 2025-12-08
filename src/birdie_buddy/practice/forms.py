from django import forms
from .models import PracticeSession


class PracticeSessionForm(forms.ModelForm):
    class Meta:
        model = PracticeSession
        fields = ["practice_type", "outcome", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4, "id": "id_notes"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["practice_type"].widget.attrs["autofocus"] = True