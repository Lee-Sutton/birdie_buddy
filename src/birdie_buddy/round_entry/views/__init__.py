from django.shortcuts import render
from .round_create_view import RoundCreateView
from .hole_create_view import HoleCreateView
from .shot_create_view import ShotCreateView

__all__ = ["RoundCreateView", "HoleCreateView", "ShotCreateView"]


# TODO: move to another app
def home(req):
    return render(req, "dashboard.html")
