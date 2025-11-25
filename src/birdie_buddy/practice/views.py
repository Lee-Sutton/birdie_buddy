from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import ListView, View
from django.shortcuts import redirect, render, get_object_or_404

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


class PracticeSessionDetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        session = get_object_or_404(PracticeSession, pk=id, user=request.user)
        context = {
            "session": session,
        }
        return render(request, "practice/practice_session_detail.html", context)


class PracticeSessionEditView(LoginRequiredMixin, View):
    def get(self, request, id):
        session = get_object_or_404(PracticeSession, pk=id, user=request.user)
        form = PracticeSessionForm(instance=session)
        return render(
            request,
            "practice/practice_session_form.html",
            {"form": form, "session": session},
        )

    def post(self, request, id):
        session = get_object_or_404(PracticeSession, pk=id, user=request.user)
        form = PracticeSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            return redirect(reverse("practice:session_detail", kwargs={"id": id}))

        return render(
            request,
            "practice/practice_session_form.html",
            {"form": form, "session": session},
        )


class PracticeSessionDeleteView(LoginRequiredMixin, View):
    def post(self, request, id):
        session = get_object_or_404(PracticeSession, pk=id, user=request.user)
        session.delete()
        response = HttpResponse(status=200)
        response["HX-Redirect"] = reverse("practice:practice_list")
        return response
    
    def delete(self, request, id):
        return self.post(request, id)
