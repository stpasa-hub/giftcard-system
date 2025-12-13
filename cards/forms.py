from django import forms


class RedeemForm(forms.Form):
    card_code = forms.CharField(
        label="Kartencode",
        max_length=32,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    amount = forms.DecimalField(
        label="Betrag",
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    reference = forms.CharField(
        label="Referenz",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )


class BalanceCheckForm(forms.Form):
    card_code = forms.CharField(
        label="Kartencode",
        max_length=32,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Kartencode eingeben"
        })
    )

