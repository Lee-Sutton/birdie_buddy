from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from birdie_buddy.round_entry.models import Round


class RoundDetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        round: Round = get_object_or_404(Round, pk=id, user=request.user)
        holes = round.hole_set.all()

        # Continue link: point to the first hole (number=1) for now.
        from django.urls import reverse

        continue_href = reverse("round_entry:create_hole", kwargs={"id": round.id, "number": 1})

        context = {
            "round": round,
            "holes": holes,
            "show_stats": round.complete,
            "continue_href": continue_href,
        }

        return render(request, "round_entry/round_detail.html", context)
