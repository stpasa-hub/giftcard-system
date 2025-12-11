from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from .models import Card, Merchant, Transaction
from .forms import RedeemForm, BalanceCheckForm


def landing_page(request):
    """
    Öffentliche Landing-Page für das Geschenkkartensystem.
    """
    return render(request, "cards/landing.html")


def merchant_login(request):
    """
    Händler-Login: nur Benutzer mit verknüpftem Merchant-Konto dürfen rein.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # prüfen, ob es zu diesem User einen Merchant gibt
            try:
                user.merchant
            except Merchant.DoesNotExist:
                messages.error(request, "Diesem Benutzer ist kein Händlerkonto zugeordnet.")
            else:
                login(request, user)
                return redirect("cards:merchant_dashboard")
        else:
            messages.error(request, "Login fehlgeschlagen. Bitte Zugangsdaten prüfen.")

    return render(request, "cards/login.html")


def merchant_logout(request):
    logout(request)
    return redirect("cards:merchant_login")


@login_required
def merchant_dashboard(request):
    """
    Dashboard für Händler:
    - Karte prüfen
    - Betrag einlösen
    - letzte Transaktionen sehen
    """
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


@login_required
def redeem_view(request):
    """
    Betrag von einer Karte abbuchen (Zahlung).
    """
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
                        active=True,
                    )

                    now = timezone.now()
                    if card.expires_at < now:
                        messages.error(request, "Karte ist abgelaufen.")
                    elif card.current_amount < amount:
                        messages.error(request, "Nicht genügend Guthaben auf der Karte.")
                    else:
                        card.current_amount -= amount
                        card.save()

                        Transaction.objects.create(
                            card=card,
                            merchant=merchant,
                            amount=amount,
                            reference=reference,
                        )

                        messages.success(
                            request,
                            f"Einlösung erfolgreich. Neues Guthaben: {card.current_amount} CHF",
                        )
            except Card.DoesNotExist:
                messages.error(request, "Karte nicht gefunden oder inaktiv.")
        else:
            messages.error(request, "Formular ungültig.")

    return redirect("cards:merchant_dashboard")


@login_required
def balance_view(request):
    """
    Guthaben einer Karte abfragen.
    Zeigt eine kleine Bestätigungsseite (verify.html) mit Kartendaten.
    """
    merchant = Merchant.objects.get(user=request.user)

    card = None
    error = None

    if request.method == "POST":
        form = BalanceCheckForm(request.POST)
        if form.is_valid():
            card_code = form.cleaned_data["card_code"]
            try:
                card = Card.objects.get(card_code=card_code, active=True)
            except Card.DoesNotExist:
                error = "Karte nicht gefunden oder inaktiv."
            else:
                now = timezone.now()
                if card.expires_at < now:
                    messages.warning(request, "Hinweis: Diese Karte ist abgelaufen.")
        else:
            error = "Formular ungültig."

        return render(
            request,
            "cards/verify.html",
            {
                "merchant": merchant,
                "card": card,
                "error": error,
            },
        )

    # Falls jemand ohne POST auf /balance/ kommt, zurück ins Dashboard:
    return redirect("cards:merchant_dashboard")
