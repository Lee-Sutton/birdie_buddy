from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.urls import reverse

from birdie_buddy.round_entry.models import Round
from birdie_buddy.round_entry.services.tiger_five import TigerFiveService
from birdie_buddy.round_entry.services.approach_stats_service import ApproachShotService


class RoundDetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        round: Round = get_object_or_404(Round, pk=id, user=request.user)
        holes = round.hole_set.all()

        # Continue link: point to the first hole (number=1) for now.
        continue_href = reverse(
            "round_entry:create_hole", kwargs={"id": round.id, "number": 1}
        )

        context = {
            "round": round,
            "holes": holes,
            "tiger": TigerFiveService().get_for_round(round),
            "approach_stats": ApproachShotService().get_for_round(round),
            "show_stats": round.complete,
            "continue_href": continue_href,
        }

        return render(request, "round_entry/round_detail.html", context)
