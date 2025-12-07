from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def root_redirect(request):
    # Startseite direkt zum Händler-Login
    return redirect("merchant_login")


urlpatterns = [
    path("", root_redirect, name="root"),
    path("admin/", admin.site.urls),
    path("merchant/", include("cards.urls")),
]

