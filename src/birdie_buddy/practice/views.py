from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, View
from django.shortcuts import redirect, render

from birdie_buddy.practice.models import PracticeSession
from .forms import PracticeSessionForm


class PracticeListview(LoginRequiredMixin, ListView):
    model = PracticeSession
    template_name = "practice/practice_list.html"
    context_object_name = "practice_sessions"
    paginate_by = 10

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class PracticeSessionCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = PracticeSessionForm()
        return render(request, "practice/practice_session_form.html", {"form": form})

    def post(self, request):
        form = PracticeSessionForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect(reverse("practice:practice_list"))
        
        return render(request, "practice/practice_session_form.html", {"form": form})
