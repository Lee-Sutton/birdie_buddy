from django.views.generic import CreateView
from django.urls import reverse

from ..models import Round
from django.contrib.auth.mixins import LoginRequiredMixin


class RoundCreateView(LoginRequiredMixin, CreateView):
    model = Round
    fields = ["course_name", "holes_played"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        id = self.get_context_data()["object"].pk
        return reverse("round_entry:create_hole", kwargs={"id": id, "number": 1})
