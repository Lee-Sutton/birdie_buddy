import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, View
from django.shortcuts import redirect, render, get_object_or_404

from birdie_buddy.practice.models import PracticeSession
from .forms import PracticeSessionForm
from .services.notes_enhancement_service import NotesEnhancementService


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


@require_http_methods(["POST"])
def enhance_notes(request):
    """
    Enhance practice session notes using LLM.
    HTMX endpoint for AJAX requests.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
        notes = data.get("notes", "")
        practice_type = data.get("practice_type", "")

        if not notes or not notes.strip():
            return JsonResponse({"error": "Notes cannot be empty"}, status=400)

        service = NotesEnhancementService()

        enhanced_notes = service.enhance_notes(notes, practice_type)

        if enhanced_notes:
            return JsonResponse({"enhanced_notes": enhanced_notes})
        else:
            return JsonResponse({"error": "Failed to enhance notes"}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request format"}, status=400)
    except Exception:
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
