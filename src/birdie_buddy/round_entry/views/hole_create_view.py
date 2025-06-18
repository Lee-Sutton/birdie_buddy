from django import forms
from django.views.generic import View
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin

from birdie_buddy.round_entry.models import Hole, Round


class HoleForm(forms.ModelForm):
    class Meta:
        model = Hole
        fields = ["par", "score", "mental_scorecard"]


class HoleCreateView(LoginRequiredMixin, View):
    def get(self, request, id, number):
        hole = self.get_object()
        context = self.get_context_data(id=id, number=number, hole=hole)

        form = HoleForm() if hole is None else HoleForm(instance=hole)

        return render(request, "round_entry/hole_form.html", {"form": form, **context})

    def post(self, request, id, number):
        hole = self.get_object()
        form = HoleForm(request.POST, instance=hole)

        if form.is_valid():
            form.instance.user = self.request.user
            form.instance.round_id = id
            form.instance.number = number
            form.save()
            return self.redirect_to_success_url()

        return render(
            request,
            "round_entry/hole_form.html",
            {
                "form": form,
                **self.get_context_data(id=id, number=number, hole=self.get_object()),
            },
        )

    def get_object(self, queryset=None):
        # First verify the round exists and belongs to the user
        get_object_or_404(Round, id=self.kwargs["id"], user=self.request.user)

        try:
            return Hole.objects.get(
                user=self.request.user,
                round_id=self.kwargs["id"],
                number=self.kwargs["number"],
            )
        except Hole.DoesNotExist:
            return None

    def get_context_data(self, *, id, number, hole):
        context = {}
        context["number"] = number
        context["id"] = id
        if hole is None:
            context["complete"] = False
        else:
            context["complete"] = hole.round.complete

        if number > 1:
            context["previous"] = reverse(
                "round_entry:create_shots",
                kwargs={"id": id, "number": number - 1},
            )
        else:
            context["previous"] = reverse("round_entry:create_round")
        return context

    def redirect_to_success_url(self):
        return redirect(reverse("round_entry:create_shots", kwargs=self.kwargs))
