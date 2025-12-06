from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import secrets

class Merchant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Card(models.Model):
    card_code = models.CharField(max_length=64, unique=True)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.card_code} ({self.current_amount} CHF)"

    @staticmethod
    def generate_code():
        return secrets.token_urlsafe(16)


class Transaction(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='transactions')
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.amount} CHF für {self.card.card_code} ({self.created_at})"
