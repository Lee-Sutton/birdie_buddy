from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Round
from django.contrib.auth.mixins import LoginRequiredMixin


def home(req):
    return render(req, "dashboard.html")


class RoundCreateView(LoginRequiredMixin, CreateView):
    model = Round
    fields = ["course_name", "holes_played"]
    success_url = reverse_lazy("round_entry:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
