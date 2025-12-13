from django.conf import settings
from django.db import models


class Merchant(models.Model):
    """
    Händler, die Guthabenkarten einlösen können.
    Verknüpft mit einem Django-User (auth_user).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="merchant",
    )
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.user.get_username()


class Card(models.Model):
    """
    Geschenkkarte / Guthabenkarte.
    """
    card_code = models.CharField(max_length=32, unique=True)
    initial_amount = models.DecimalField(max_digits=8, decimal_places=2)
    current_amount = models.DecimalField(max_digits=8, decimal_places=2)
    bonus_points = models.IntegerField(default=0)  # Bonus-System
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.card_code} ({self.current_amount} CHF)"


class Transaction(models.Model):
    """
    Einlösung / Zahlung mit einer Karte bei einem Händler.
    """
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} CHF – {self.card.card_code} – {self.merchant}"


class BonusTransaction(models.Model):
    """
    Historie der Bonusbewegungen (Gutschrift / Einlösung von Punkten).
    """
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="bonus_transactions",
    )
    points = models.IntegerField()  # +10 für Gutschrift, -10 für Einlösung
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.points >= 0 else ""
        return f"{sign}{self.points} Punkte – {self.card.card_code}"

