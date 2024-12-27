from django.views.generic import CreateView
from django.urls import reverse
from django.views.generic.edit import UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from birdie_buddy.round_entry.models import Hole


class HoleCreateView(LoginRequiredMixin, CreateView, UpdateView):
    model = Hole
    fields = ["score", "mental_scorecard"]

    def get_object(self, queryset=None):
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
