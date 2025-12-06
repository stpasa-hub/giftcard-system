from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.merchant_login, name='merchant_login'),
    path('logout/', views.merchant_logout, name='merchant_logout'),
    path('', views.merchant_dashboard, name='merchant_dashboard'),
    path('redeem/', views.redeem_view, name='redeem'),
    path('balance/', views.balance_view, name='balance'),
]

