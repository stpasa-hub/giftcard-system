from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse

from .models import Card, Merchant, Transaction, BonusTransaction
from .forms import RedeemForm, BalanceCheckForm

from django import forms
# -------------------------------------------------------------
# LANDING PAGE (Startseite für alle Benutzer)
# -------------------------------------------------------------
def landing_page(request):
    return render(request, "cards/landing.html")

def system_info(request):
    """
    Info-Seite für Vorstand / Projekt.
    """
    return render(request, "cards/system_info.html")

# -------------------------------------------------------------
# HÄNDLER LOGIN / LOGOUT
# -------------------------------------------------------------
def merchant_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Nur zulässig, wenn ein Merchant verknüpft ist
            try:
                user.merchant
            except Merchant.DoesNotExist:
                messages.error(request, "Diesem Benutzer ist kein Händlerkonto zugeordnet.")
            else:
                login(request, user)
                return redirect("merchant_dashboard")
        else:
            messages.error(request, "Login fehlgeschlagen.")

    return render(request, "cards/login.html")


def merchant_logout(request):
    logout(request)
    return redirect("merchant_login")


# -------------------------------------------------------------
# HÄNDLER DASHBOARD
# -------------------------------------------------------------
@login_required
def merchant_dashboard(request):
    merchant = Merchant.objects.get(user=request.user)

    redeem_form = RedeemForm()
    balance_form = BalanceCheckForm()
    transactions = Transaction.objects.filter(
        merchant=merchant
    ).order_by("-created_at")[:10]

    return render(request, "cards/dashboard.html", {
        "merchant": merchant,
        "redeem_form": redeem_form,
        "balance_form": balance_form,
        "transactions": transactions,
    })


# -------------------------------------------------------------
# BETRAG EINLÖSEN (mit Bonus-System)
# -------------------------------------------------------------
@login_required
def redeem_view(request):
    merchant = Merchant.objects.get(user=request.user)

    if request.method == "POST":
        form = RedeemForm(request.POST)
        if form.is_valid():
            card_code = form.cleaned_data["card_code"]
            amount = form.cleaned_data["amount"]
            reference = form.cleaned_data["reference"]

            try:
                with transaction.atomic():
                    card = Card.objects.select_for_update().get(
                        card_code=card_code,
                        active=True
                    )

                    now = timezone.now()

                    if card.expires_at and card.expires_at < now:
                        messages.error(request, "Karte ist abgelaufen.")
                    elif card.current_amount < amount:
                        messages.error(request, "Nicht genügend Guthaben auf der Karte.")
                    else:
                        # Guthaben abbuchen
                        card.current_amount -= amount
                        card.save()

                        # Zahlung speichern
                        Transaction.objects.create(
                            card=card,
                            merchant=merchant,
                            amount=amount,
                            reference=reference,
                        )

                        # BONUS-SYSTEM: 1 Punkt pro 10 CHF
                        bonus_points = int(amount // 10)
                        if bonus_points > 0:
                            BonusTransaction.objects.create(
                                card=card,
                                merchant=merchant,
                                points_change=bonus_points,
                                reason=f"Bonus für Einlösung von {amount} CHF bei {merchant.name}",
                            )

                        messages.success(
                            request,
                            f"Einlösung erfolgreich. Neues Guthaben: {card.current_amount} CHF "
                            f"(+{bonus_points} Bonuspunkte)"
                        )

            except Card.DoesNotExist:
                messages.error(request, "Karte nicht gefunden oder inaktiv.")
        else:
            messages.error(request, "Formular ungültig.")

    return redirect("merchant_dashboard")


# -------------------------------------------------------------
# GUTHABEN ABFRAGEN
# -------------------------------------------------------------
@login_required
def balance_view(request):
    if request.method == "POST":
        form = BalanceCheckForm(request.POST)

        if form.is_valid():
            card_code = form.cleaned_data["card_code"]

            try:
                card = Card.objects.get(card_code=card_code, active=True)
            except Card.DoesNotExist:
                messages.error(request, "Karte nicht gefunden oder inaktiv.")
            else:
                now = timezone.now()

                if card.expires_at and card.expires_at < now:
                    messages.warning(request, "Karte ist abgelaufen.")

                messages.info(
                    request,
                    f"Guthaben: {card.current_amount} CHF – Bonuspunkte: {card.bonus_points}"
                )
        else:
            messages.error(request, "Formular ungültig.")

    return redirect("merchant_dashboard")


# -------------------------------------------------------------
# KÄUFER-BONUSCENTER (kein Login)
# -------------------------------------------------------------
class PublicCardLookupForm(forms.Form):
    card_code = forms.CharField(label="Kartencode", max_length=32)

def bonus_home(request):
    """
    Einstieg für Kund:innen: Kartencode eingeben.
    """
    form = PublicCardLookupForm(request.GET or None)
    card = None
    if form.is_valid():
        code = form.cleaned_data["card_code"]
        try:
            card = Card.objects.get(card_code=code, active=True)
        except Card.DoesNotExist:
            card = None

    return render(request, "cards/bonus_home.html", {
        "form": form,
        "card": card,
    })

# -------------------------------------------------------------
# API ENDPOINT: Kartendetails (JSON)
# -------------------------------------------------------------
def api_card_detail(request, card_code):
    try:
        card = Card.objects.get(card_code=card_code, active=True)
    except Card.DoesNotExist:
        return JsonResponse({"error": "not_found"}, status=404)

    data = {
        "card_code": card.card_code,
        "current_amount": float(card.current_amount),
        "bonus_points": card.bonus_points,
        "expires_at": card.expires_at.isoformat() if card.expires_at else None,
        "active": card.active,
    }
    return JsonResponse(data)


# -------------------------------------------------------------
# API ENDPOINT: Händler-Transaktionen (JSON)
# -------------------------------------------------------------
@login_required
def api_merchant_transactions(request):
    merchant = Merchant.objects.get(user=request.user)

    qs = Transaction.objects.filter(
        merchant=merchant
    ).order_by("-created_at")[:50]

    data = [
        {
            "card_code": tx.card.card_code,
            "amount": float(tx.amount),
            "reference": tx.reference,
            "created_at": tx.created_at.isoformat(),
        }
        for tx in qs
    ]

    return JsonResponse({"transactions": data})

