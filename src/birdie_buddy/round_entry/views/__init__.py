from django.shortcuts import render
from .round_create_view import RoundCreateView
from .hole_create_view import HoleCreateView
from .shot_create_view import ShotCreateView
from .round_detail_view import RoundDetailView

__all__ = ["RoundCreateView", "HoleCreateView", "ShotCreateView", "RoundDetailView"]


# TODO: move to another app
def home(req):
    return render(req, "dashboard.html")
