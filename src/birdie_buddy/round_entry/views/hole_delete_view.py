from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from birdie_buddy.round_entry.models import Hole, Round


class HoleDeleteView(LoginRequiredMixin, View):
    def delete(self, request, round_id: int, hole_id: int) -> HttpResponse:
        get_object_or_404(Round, id=round_id, user=request.user)

        hole = get_object_or_404(
            Hole,
            id=hole_id,
            round_id=round_id,
            user=request.user,
        )
        hole.delete()

        response = HttpResponse(status=200)
        response["HX-Trigger"] = "holeDeleted"
        return response
