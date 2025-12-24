from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from birdie_buddy.round_entry.models import Hole
from birdie_buddy.round_entry.services.hole_service import HoleService


class HoleDeleteView(LoginRequiredMixin, View):
    def delete(self, request, hole_id: int) -> HttpResponse:
        # Get hole and verify it belongs to user (round ownership is implicit)
        hole = get_object_or_404(
            Hole,
            id=hole_id,
            user=request.user,
        )

        # Delegate business logic to service
        HoleService.delete_hole(hole)

        response = HttpResponse(status=200)
        response["HX-Trigger"] = "holeDeleted"
        return response
