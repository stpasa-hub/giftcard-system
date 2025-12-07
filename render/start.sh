#!/usr/bin/env bash
set -o errexit

# Erzeuge Superuser + Händler, wenn noch nicht vorhanden
python manage.py shell <<EOF
from django.contrib.auth.models import User
from cards.models import Merchant

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "Admin123!")
    print(">>> Superuser admin erstellt (Passwort: Admin123!)")

if not User.objects.filter(username="merchant").exists():
    u = User.objects.create_user("merchant", password="Merchant123!")
    Merchant.objects.create(user=u, name="Test Laden Stein am Rhein")
    print(">>> Händler 'merchant' erstellt (Passwort: Merchant123!)")
EOF

# Gunicorn für Produktion starten
gunicorn giftcard.wsgi:application --bind 0.0.0.0:$PORT
