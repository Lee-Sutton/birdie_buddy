from django.views.generic import View
from django.urls import reverse
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from birdie_buddy.round_entry.models import ScorecardUpload
from birdie_buddy.round_entry.forms import ScorecardUploadForm


class ScorecardUploadView(LoginRequiredMixin, View):
    def get(self, request):
        form = ScorecardUploadForm()
        context = self.get_context_data()
        return render(
            request, "round_entry/scorecard_upload.html", {"form": form, **context}
        )

    def post(self, request):
        form = ScorecardUploadForm(request.POST, request.FILES)

        if form.is_valid():
            ScorecardUpload.objects.create(
                user=self.request.user,
                course_name=form.cleaned_data["course_name"],
                scorecard_image=form.cleaned_data["scorecard_image"],
            )
            return self.redirect_to_success_url()

        messages.error(
            self.request,
            "There was an error uploading your scorecard. Please check form and try again.",
        )
        context = self.get_context_data()
        return render(
            request, "round_entry/scorecard_upload.html", {"form": form, **context}
        )

    def get_context_data(self):
        context = {}
        context["previous"] = reverse("round_entry:round_list")
        return context

    def redirect_to_success_url(self):
        return redirect(reverse("round_entry:round_list"))
