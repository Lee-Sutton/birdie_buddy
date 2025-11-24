from django.urls import path
from . import views

app_name = "practice"

urlpatterns = [
    path("", views.PracticeListview.as_view(), name="list"),
]
