from django.urls import path
from . import views

app_name = "round_entry"

urlpatterns = [
    path("", views.home, name="home"),
    path("rounds/create", views.RoundCreateView.as_view(), name="create")
]
