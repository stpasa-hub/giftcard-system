from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from .models import Card, Merchant, Transaction
from .forms import RedeemForm, BalanceCheckForm


def merchant_login(request):
    """
    Händler-Login: nur Benutzer mit zugehörigem Merchant dürfen rein.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # prüfen, ob User ein Merchant ist
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


@login_required
def merchant_dashboard(request):
    """
    Händler-Dashboard:
      - Einlösung
      - Guthabenprüfung
      - letzte Transaktionen
    """
    merchant = Merchant.objects.get(user=request.user)

    # Optional: Kartencode aus QR/link vorbefüllen (?card=...)
    card_code_prefill = request.GET.get("card")

    redeem_initial = {}
    balance_initial = {}
    if card_code_prefill:
        redeem_initial["card_code"] = card_code_prefill
        balance_initial["card_code"] = card_code_prefill

    redeem_form = RedeemForm(initial=redeem_initial)
    balance_form = BalanceCheckForm(initial=balance_initial)

    transactions = Transaction.objects.filter(
        merchant=merchant
    ).order_by("-created_at")[:10]

    return render(
        request,
        "cards/dashboard.html",
        {
            "merchant": merchant,
            "redeem_form": redeem_form,
            "balance_form": balance_form,
            "transactions": transactions,
        },
    )


@login_required
def redeem_view(request):
    """
    Betrag von einer Karte abbuchen (Zahlung).
    Zeigt bei Erfolg die Seite cards/redeem.html.
    """
    merchant = Merchant.objects.get(user=request.user)

    if request.method != "POST":
        return redirect("merchant_dashboard")

    form = RedeemForm(request.POST)
    if not form.is_valid():
        error = "Formular ungültig."
        return render(
            request,
            "cards/redeem.html",
            {"card": None, "amount": None, "error": error},
        )

    card_code = form.cleaned_data["card_code"]
    amount = form.cleaned_data["amount"]
    reference = form.cleaned_data["reference"]

    try:
        with transaction.atomic():
            card = (
                Card.objects.select_for_update()
                .get(card_code=card_code, active=True)
            )

            now = timezone.now()
            if card.expires_at < now:
                error = "Karte ist abgelaufen."
                return render(
                    request,
                    "cards/redeem.html",
                    {"card": card, "amount": None, "error": error},
                )

            if card.current_amount < amount:
                error = "Nicht genügend Guthaben auf der Karte."
                return render(
                    request,
                    "cards/redeem.html",
                    {"card": card, "amount": None, "error": error},
                )

            # Alles ok -> abbuchen
            card.current_amount -= amount
            card.save()

            Transaction.objects.create(
                card=card,
                merchant=merchant,
                amount=amount,
                reference=reference,
            )

    except Card.DoesNotExist:
        error = "Karte nicht gefunden oder inaktiv."
        return render(
            request,
            "cards/redeem.html",
            {"card": None, "amount": None, "error": error},
        )

    # Erfolg
    return render(
        request,
        "cards/redeem.html",
        {
            "card": card,
            "amount": amount,
            "error": None,
        },
    )


@login_required
def balance_view(request):
    """
    Guthaben einer Karte abfragen.
    Zeigt Ergebnis auf cards/verify.html.
    """
    if request.method != "POST":
        return redirect("merchant_dashboard")

    form = BalanceCheckForm(request.POST)
    if not form.is_valid():
        error = "Formular ungültig."
        return render(
            request,
            "cards/verify.html",
            {"card": None, "error": error},
        )

    card_code = form.cleaned_data["card_code"]

    try:
        card = Card.objects.get(card_code=card_code, active=True)
    except Card.DoesNotExist:
        error = "Karte nicht gefunden oder inaktiv."
        return render(
            request,
            "cards/verify.html",
            {"card": None, "error": error},
        )

    error = None
    now = timezone.now()
    if card.expires_at < now:
        error = "Karte ist abgelaufen."

    return render(
        request,
        "cards/verify.html",
        {
            "card": card,
            "error": error,
        },
    )

