from django.urls import path
from . import views

app_name = "practice"

urlpatterns = [
    path("", views.PracticeListview.as_view(), name="practice_list"),
    path("create/", views.PracticeSessionCreateView.as_view(), name="create_session"),
    path("<int:id>/", views.PracticeSessionDetailView.as_view(), name="session_detail"),
    path("<int:id>/edit/", views.PracticeSessionEditView.as_view(), name="edit_session"),
    path("<int:id>/delete/", views.PracticeSessionDeleteView.as_view(), name="delete_session"),
    path("enhance-notes/", views.enhance_notes, name="enhance_notes"),
]
