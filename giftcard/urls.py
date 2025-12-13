from django.contrib import admin
from django.urls import path
from cards import views as cards_views
from cards import views as cards_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", cards_views.landing_page, name="landing"),

    path("system-info/", cards_views.system_info, name="system_info"),

    # Kundencenter / Bonus
    path("bonus/", cards_views.bonus_home, name="bonus_home"),

    # Info-Seite für Vorstand / Projekt
    path("system-info/", cards_views.system_info, name="system_info"),

    # Händler-Bereich
    path("merchant/login/", cards_views.merchant_login, name="merchant_login"),
    path("merchant/logout/", cards_views.merchant_logout, name="merchant_logout"),
    path("merchant/dashboard/", cards_views.merchant_dashboard, name="merchant_dashboard"),
    path("merchant/redeem/", cards_views.redeem_view, name="redeem"),
    path("merchant/balance/", cards_views.balance_view, name="balance"),
]

