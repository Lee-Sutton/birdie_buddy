from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from birdie_buddy.round_entry.models import Round


class RoundListView(LoginRequiredMixin, ListView):
    model = Round
    template_name = "round_entry/round_list.html"
    context_object_name = "rounds"
    paginate_by = 10

    def get_queryset(self):
        return Round.objects.filter(user=self.request.user).order_by("-created_at")
