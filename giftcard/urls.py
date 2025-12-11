from django.contrib import admin
from django.urls import path, include
from cards import views as cards_views

urlpatterns = [
    # Admin-Backend
    path("admin/", admin.site.urls),

    # Öffentliche Landingpage unter /
    path("", cards_views.landing_page, name="landing"),

    # Händler-Bereich unter /merchant/...
    path("merchant/", include(("cards.urls", "cards"), namespace="cards")),
]

