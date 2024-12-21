from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", include("birdie_buddy.round_entry.urls")),
    path("users/", include("birdie_buddy.users.urls")),
]
