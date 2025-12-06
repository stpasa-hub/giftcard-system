from django import forms

class RedeemForm(forms.Form):
    card_code = forms.CharField(
        label="Kartencode",
        max_length=64,
        widget=forms.TextInput(attrs={"id": "redeem_card_code"})
    )
    amount = forms.DecimalField(
        label="Betrag (CHF)",
        max_digits=10,
        decimal_places=2
    )
    reference = forms.CharField(
        label="Referenz / Belegnummer",
        max_length=255,
        required=False
    )


class BalanceCheckForm(forms.Form):
    card_code = forms.CharField(
        label="Kartencode",
        max_length=64,
        widget=forms.TextInput(attrs={"id": "balance_card_code"})
    )

