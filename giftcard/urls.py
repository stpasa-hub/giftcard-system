from django.contrib import admin
from django.urls import path
from cards import views as cards_views

urlpatterns = [
    # Admin-Backend
    path("admin/", admin.site.urls),

    # Öffentliche Landingpage unter /
    path("", cards_views.landing_page, name="landing"),

    # Händler-Bereich
    path("merchant/login/", cards_views.merchant_login, name="merchant_login"),
    path("merchant/logout/", cards_views.merchant_logout, name="merchant_logout"),
    path("merchant/dashboard/", cards_views.merchant_dashboard, name="merchant_dashboard"),
    path("merchant/redeem/", cards_views.redeem_view, name="redeem"),
    path("merchant/balance/", cards_views.balance_view, name="balance"),
]

