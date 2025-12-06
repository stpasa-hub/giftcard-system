from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Card, Merchant, Transaction

admin.site.register(Card)
admin.site.register(Merchant)
admin.site.register(Transaction)
