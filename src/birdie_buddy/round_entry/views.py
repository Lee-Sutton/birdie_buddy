from django.shortcuts import render


def home(req):
    render(req, "dashboard.html")
