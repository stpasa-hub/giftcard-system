from django.contrib import admin
from .models import Card, Merchant, Transaction, BonusTransaction


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("card_code", "current_amount", "bonus_points", "active", "expires_at")
    search_fields = ("card_code",)
    list_filter = ("active",)


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "user__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("card", "merchant", "amount", "created_at", "reference")
    search_fields = ("card__card_code", "merchant__name", "reference")


@admin.register(BonusTransaction)
class BonusTransactionAdmin(admin.ModelAdmin):
    list_display = ("card", "points", "reason", "created_at")
    search_fields = ("card__card_code", "reason")

