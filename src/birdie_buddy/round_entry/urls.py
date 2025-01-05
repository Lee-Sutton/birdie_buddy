from django.urls import path
from . import views

app_name = "round_entry"

urlpatterns = [
    path("", views.home, name="home"),
    path("rounds/create", views.RoundCreateView.as_view(), name="create_round"),
    path(
        "rounds/<int:id>/holes/<int:number>/create",
        views.HoleCreateView.as_view(),
        name="create_hole",
    ),
    path(
        "rounds/<int:id>/holes/<int:number>/shots/create",
        views.ShotCreateView.as_view(),
        name="create_shots",
    ),
    path(
        "rounds/<int:id>",
        views.RoundDetailView.as_view(),
        name="round_detail",
    ),
]
