from django.shortcuts import render


def stats_view(req):
    pass
    return render(
        req,
        "stats.html",
        {
            "strokes_gained_driving": 2,
            "strokes_gained_approach": 2,
            "strokes_gained_putting": 2,
            "strokes_gained_around_the_green": 2,
        },
    )
