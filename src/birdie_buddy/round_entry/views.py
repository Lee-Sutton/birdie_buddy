from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView
from django.urls import reverse
from django.views.generic.base import View
from django.forms import formset_factory
from django.views.generic.edit import UpdateView

from birdie_buddy.round_entry.forms import ShotForm
from .models import Hole, Round
from django.contrib.auth.mixins import LoginRequiredMixin


def home(req):
    return render(req, "dashboard.html")


class RoundCreateView(LoginRequiredMixin, CreateView):
    model = Round
    fields = ["course_name", "holes_played"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        id = self.get_context_data()["object"].pk
        return reverse("round_entry:create_hole", kwargs={"id": id, "number": 1})


class HoleCreateView(LoginRequiredMixin, CreateView, UpdateView):
    model = Hole
    fields = ["score", "mental_scorecard"]

    def get_object(self, queryset=None):
        # Try to get existing hole first
        # TODO: enforce on the database as well
        try:
            return Hole.objects.get(
                user=self.request.user,
                round_id=self.kwargs["id"],
                number=self.kwargs["number"],
            )
        except Hole.DoesNotExist:
            return None

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.round_id = self.kwargs["id"]
        form.instance.number = self.kwargs["number"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["number"] = self.kwargs["number"]
        return context

    def get_success_url(self):
        return reverse("round_entry:create_shots", kwargs=self.kwargs)


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
            # TODO: handle when the round is finished
            url = reverse(
                "round_entry:create_hole", kwargs={"id": id, "number": number + 1}
            )
            return redirect(url)

        return render(request, "round_entry/shots_form.html", {"formset": formset})

    def get(self, request, id, number):
        hole = get_object_or_404(
            Hole, user=self.request.user, number=number, round_id=id
        )

        ShotFormSet = formset_factory(ShotForm, extra=0)
        formset = ShotFormSet(initial=[{} for _ in range(hole.score)])

        return render(
            request,
            "round_entry/shots_form.html",
            {
                "formset": formset,
                "number": number,
                "shot_count": range(1, hole.score + 1),
            },
        )
