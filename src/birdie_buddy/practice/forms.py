from django import forms
from .models import PracticeSession


class PracticeSessionForm(forms.ModelForm):
    class Meta:
        model = PracticeSession
        fields = ["practice_type", "outcome", "notes"]
        widgets = {
            # Textarea - EasyMDE will attach to this in the template
            "notes": forms.Textarea(attrs={"id": "id_notes", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["practice_type"].widget.attrs["autofocus"] = True