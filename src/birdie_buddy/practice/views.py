from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from birdie_buddy.practice.models import PracticeSession


class PracticeListview(LoginRequiredMixin, ListView):
    model = PracticeSession
    template_name = "practice/practice_list.html"
    context_object_name = "practice_sessions"
    paginate_by = 10

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
