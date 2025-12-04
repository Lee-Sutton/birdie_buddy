import logging

from django.views.generic import View
from django.urls import reverse
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin

from birdie_buddy.round_entry.models import ScorecardUpload
from birdie_buddy.round_entry.forms import ScorecardUploadForm
from birdie_buddy.round_entry.services.scorecard_parser_service import (
    ScorecardParserService,
)

logger = logging.getLogger(__name__)


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
            scorecard_upload = ScorecardUpload.objects.create(
                user=self.request.user,
                course_name=form.cleaned_data["course_name"],
                scorecard_image=form.cleaned_data["scorecard_image"],
            )

            # Parse the uploaded scorecard image
            parser_service = ScorecardParserService()
            parsed_text = parser_service.parse_scorecard_image(
                scorecard_upload.scorecard_image
            )

            if parsed_text:
                logger.info(
                    f"Scorecard parsed for user {request.user.id}, "
                    f"upload {scorecard_upload.id}. Extracted text:\n{parsed_text['text']}"
                )
            else:
                logger.warning(
                    f"Scorecard parsing failed for user {request.user.id}, "
                    f"upload {scorecard_upload.id}"
                )

            return self.redirect_to_success_url()

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
