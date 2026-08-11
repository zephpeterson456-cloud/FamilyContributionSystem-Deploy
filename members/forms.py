from django import forms
from .models import Contributor, Family, Payment, SystemSettings

class ContributorForm(forms.ModelForm):
    class Meta:
        model = Contributor
        fields = [
            "family",
            "full_name",
            "phone",
            "email",
            "amount_expected",
            "is_active",
        ]

        widgets = {
            "family": forms.Select(attrs={"class": "form-select"}),

            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter full name"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email"
            }),

            "amount_expected": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }
from .models import Family

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ["name", "account_number"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Family Name"
            }),

            "account_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Account Number"
            }),
        }
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "contributor",
            "amount",
            "payment_method",
            "remarks",
        ]

        widgets = {
            "contributor": forms.Select(attrs={
                "class": "form-select"
            }),

            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Amount Paid"
            }),

            "payment_method": forms.Select(attrs={
                "class": "form-select"
            }),

            "remarks": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional remarks"
            }),
        }
from .models import Beneficiary

class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = [
            "contributor",
            "full_name",
            "relationship",
            "phone",
            "is_active",
        ]

        widgets = {
            "contributor": forms.Select(attrs={
                "class": "form-select"
            }),

            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Beneficiary Full Name"
            }),

            "relationship": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Relationship"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone Number"
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }
class SettingsForm(forms.ModelForm):

    class Meta:
        model = SystemSettings

        fields = [
            "organization_name",
            "monthly_contribution",
            "mpesa_shortcode",
            "mpesa_consumer_key",
            "mpesa_consumer_secret",
            "mpesa_passkey",
        ]

        widgets = {

            "organization_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "monthly_contribution": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "mpesa_shortcode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "174379"
                }
            ),

            "mpesa_consumer_key": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "M-Pesa Consumer Key"
                }
            ),

            "mpesa_consumer_secret": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "M-Pesa Consumer Secret"
                }
            ),

            "mpesa_passkey": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "M-Pesa Passkey"
                }
            ),
        }
