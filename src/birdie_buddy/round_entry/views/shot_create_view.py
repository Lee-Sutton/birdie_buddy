from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import View
from django.forms import formset_factory

from birdie_buddy.round_entry.forms import ShotForm, ShotFormSetHelper
from birdie_buddy.round_entry.models import Hole, Round
from birdie_buddy.round_entry.services.shot_service import ShotService
from django.contrib.auth.mixins import LoginRequiredMixin


class ShotCreateView(LoginRequiredMixin, View):
    def post(self, request, id, number):
        hole = self.get_hole()
        ShotFormSet = formset_factory(ShotForm, extra=0)
        formset = ShotFormSet(request.POST)

        if formset.is_valid():
            ShotService.create_shots_for_hole(hole, request.user, formset)
            url = self.get_success_url(hole.round, id, number)
            return redirect(url)

        return self.render(formset, hole)

    def get(self, request, id, number):
        hole = self.get_hole()
        shots = [
            {"start_distance": shot.start_distance, "lie": shot.lie}
            for shot in hole.shot_set.all().order_by("number")
        ]

        ShotFormSet = formset_factory(ShotForm, extra=0)
        formset = ShotFormSet(
            initial=[get_from_list(shots, i, {}) for i in range(hole.score)]
        )

        number = self.kwargs["number"]
        id = self.kwargs["id"]
        return render(
            self.request,
            "round_entry/shots_form.html",
            {
                "formset": formset,
                "complete": hole.round.complete,
                "helper": ShotFormSetHelper(),
                "number": self.kwargs["number"],
                "id": self.kwargs["id"],
                "previous": reverse(
                    "round_entry:create_hole", kwargs={"id": id, "number": number}
                ),
            },
        )

    def get_hole(self):
        number = self.kwargs["number"]
        id = self.kwargs["id"]

        return get_object_or_404(
            Hole, user=self.request.user, number=number, round_id=id
        )

    def render(self, formset, hole):
        number = self.kwargs["number"]
        id = self.kwargs["id"]
        return render(
            self.request,
            "round_entry/shots_form.html",
            {
                "formset": formset,
                "complete": hole.round.complete,
                "helper": ShotFormSetHelper(),
                "number": self.kwargs["number"],
                "id": self.kwargs["id"],
                "previous": reverse(
                    "round_entry:create_hole", kwargs={"id": id, "number": number}
                ),
            },
        )

    def get_success_url(self, round: Round, id, number):
        if number >= round.holes_played:
            return reverse("round_entry:round_detail", kwargs={"id": id})

        return reverse(
            "round_entry:create_hole", kwargs={"id": id, "number": number + 1}
        )


# TODO: extract to utils
def get_from_list(lst, idx, default=None):
    try:
        return lst[idx]
    except IndexError:
        return default
