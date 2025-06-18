from django.views.generic import CreateView
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from birdie_buddy.round_entry.models import Hole, Round


class HoleCreateView(LoginRequiredMixin, CreateView, UpdateView):
    model = Hole
    fields = ["par", "score", "mental_scorecard"]

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

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.round_id = self.kwargs["id"]
        form.instance.number = self.kwargs["number"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        number = self.kwargs["number"]
        id = self.kwargs["id"]

        context["number"] = number
        context["id"] = id
        if number > 1:
            context["previous"] = reverse(
                "round_entry:create_shots",
                kwargs={"id": id, "number": number - 1},
            )
        else:
            context["previous"] = reverse("round_entry:create_round")
        return context

    def get_success_url(self):
        return reverse("round_entry:create_shots", kwargs=self.kwargs)
