from django.urls import path
from . import views

app_name = "practice"

urlpatterns = [
    path("", views.PracticeListview.as_view(), name="practice_list"),
    path("create/", views.PracticeSessionCreateView.as_view(), name="create_session"),
]
