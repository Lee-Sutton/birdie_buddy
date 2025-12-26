from django.http import HttpResponse
from django.template.loader import render_to_string
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

        # Get round and scorecard_upload before deleting
        round_obj = hole.round
        scorecard_upload = getattr(round_obj, 'scorecardupload', None)

        # Delegate business logic to service
        HoleService.delete_hole(hole)

        # Get updated holes list (with renumbered holes)
        holes = Hole.objects.filter(round=round_obj).order_by('number')

        # Render the updated holes grid
        html = render_to_string(
            'round_entry/_holes_grid.html',
            {
                'holes': holes,
                'round': round_obj,
                'scorecard_upload': scorecard_upload,
            },
            request=request
        )

        return HttpResponse(html)
