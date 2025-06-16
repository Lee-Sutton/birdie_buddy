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
        hole: Hole = get_object_or_404(
            Hole, user=self.request.user, number=number, round_id=id
        )
        ShotFormSet = formset_factory(ShotForm, extra=0)
        formset = ShotFormSet(request.POST)

        if formset.is_valid():
            ShotService.create_shots_for_hole(hole, request.user, formset)
            url = self.get_success_url(hole.round, id, number)
            return redirect(url)

        return render(
            request,
            "round_entry/shots_form.html",
            {"formset": formset, "helper": ShotFormSetHelper(), "number": number},
        )

    def get(self, request, id, number):
        hole = get_object_or_404(
            Hole, user=self.request.user, number=number, round_id=id
        )

        ShotFormSet = formset_factory(ShotForm, extra=0)
        formset = ShotFormSet(initial=[{} for _ in range(hole.score)])
        helper = ShotFormSetHelper()

        return render(
            request,
            "round_entry/shots_form.html",
            {
                "formset": formset,
                "helper": helper,
                "number": number,
            },
        )

    def get_success_url(self, round: Round, id, number):
        if number >= round.holes_played:
            return reverse("round_entry:round_detail", kwargs={"id": id})

        return reverse(
            "round_entry:create_hole", kwargs={"id": id, "number": number + 1}
        )
