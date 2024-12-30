from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import View
from django.forms import formset_factory

from birdie_buddy.round_entry.forms import ShotForm, ShotFormSetHelper
from ..models import Hole
from django.contrib.auth.mixins import LoginRequiredMixin


class ShotCreateView(LoginRequiredMixin, View):
    def post(self, request, id, number):
        hole = get_object_or_404(
            Hole, user=self.request.user, number=number, round_id=id
        )
        ShotFormSet = formset_factory(ShotForm, extra=0)
        formset = ShotFormSet(request.POST)

        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    shot = form.save(commit=False)
                    shot.hole = hole
                    shot.user = request.user
                    shot.save()
            url = reverse(
                "round_entry:create_hole", kwargs={"id": id, "number": number + 1}
            )
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
