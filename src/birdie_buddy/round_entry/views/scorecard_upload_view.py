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
from birdie_buddy.round_entry.services.scorecard_import_service import (
    ScorecardImportService,
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
            scorecard_data, raw_json = parser_service.parse_scorecard_image(
                scorecard_upload.scorecard_image
            )

            # Save the raw JSON data for debugging
            if raw_json:
                scorecard_upload.parsed_data = raw_json
                scorecard_upload.save()

            # Create Round/Hole/Shot objects if parsing succeeded
            if scorecard_data:
                import_service = ScorecardImportService()
                round_obj = import_service.create_round_from_scorecard_data(
                    user=request.user,
                    scorecard_upload=scorecard_upload,
                    scorecard_data=scorecard_data,
                )

                if round_obj:
                    logger.info(
                        f"Scorecard parsed and round created for user {request.user.id}, "
                        f"round {round_obj.id}"
                    )
                else:
                    logger.error(
                        f"Failed to create round from parsed data for user {request.user.id}, "
                        f"upload {scorecard_upload.id}"
                    )
            else:
                logger.warning(
                    f"Scorecard parsing failed for user {request.user.id}, "
                    f"upload {scorecard_upload.id}"
                )

            return self.redirect_to_success_url(scorecard_upload.id)

        context = self.get_context_data()
        return render(
            request, "round_entry/scorecard_upload.html", {"form": form, **context}
        )

    def get_context_data(self):
        context = {}
        context["previous"] = reverse("round_entry:round_list")
        return context

    def redirect_to_success_url(self, scorecard_upload_id):
        return redirect(
            reverse(
                "round_entry:scorecard_review",
                kwargs={"scorecard_upload_id": scorecard_upload_id},
            )
        )
