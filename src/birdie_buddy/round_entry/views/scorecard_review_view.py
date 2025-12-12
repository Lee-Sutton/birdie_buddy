from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import View

from birdie_buddy.round_entry.models import ScorecardUpload


class ScorecardReviewView(LoginRequiredMixin, View):
    """View for reviewing parsed scorecard data before finalizing."""

    def get(self, request, scorecard_upload_id):
        scorecard_upload = get_object_or_404(
            ScorecardUpload, pk=scorecard_upload_id, user=request.user
        )

        # Check if parsing was successful
        parsing_failed = scorecard_upload.round is None

        context = {
            "scorecard_upload": scorecard_upload,
            "parsing_failed": parsing_failed,
        }

        if not parsing_failed:
            round_obj = scorecard_upload.round
            holes = round_obj.hole_set.prefetch_related("shot_set").order_by("number")

            context.update(
                {
                    "round": round_obj,
                    "holes": holes,
                    "round_detail_url": reverse(
                        "round_entry:round_detail", kwargs={"id": round_obj.id}
                    ),
                }
            )
        else:
            context["manual_entry_url"] = reverse("round_entry:create_round")

        return render(request, "round_entry/scorecard_review.html", context)
