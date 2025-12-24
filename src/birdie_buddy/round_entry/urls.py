from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "round_entry"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(url="/analytics", permanent=False),
        name="home_redirect",
    ),
    path("analytics", views.stats_view, name="home"),
    path("rounds/", views.RoundListView.as_view(), name="round_list"),
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
    path(
        "rounds/upload-scorecard",
        views.ScorecardUploadView.as_view(),
        name="upload_scorecard",
    ),
    path(
        "rounds/scorecard/<int:scorecard_upload_id>/review",
        views.ScorecardReviewView.as_view(),
        name="scorecard_review",
    ),
    path(
        "holes/<int:hole_id>/delete",
        views.HoleDeleteView.as_view(),
        name="delete_hole",
    ),
]
