from django import forms
from .models import Contributor, Family, Payment, SystemSettings
from .models import ContributionObligation, Loan, LoanRepayment


class ContributionObligationForm(forms.ModelForm):
    class Meta:
        model = ContributionObligation
        fields = [
            "contributor",
            "beneficiary",
            "amount",
            "frequency",
            "start_date",
            "end_date",
            "is_active",
            "notes",
        ]

        widgets = {
            "contributor": forms.Select(
                attrs={"class": "form-select"}
            ),

            "beneficiary": forms.Select(
                attrs={"class": "form-select"}
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "100",
                    "step": "0.01",
                }
            ),

            "frequency": forms.Select(
                attrs={"class": "form-select"}
            ),

            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional notes",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        contributor = cleaned_data.get("contributor")
        beneficiary = cleaned_data.get("beneficiary")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if beneficiary and contributor:
            if beneficiary.contributor_id != contributor.id:
                raise forms.ValidationError(
                    "The selected beneficiary does not belong to this contributor."
                )

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                "End date cannot be earlier than the start date."
            )

        return cleaned_data


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = [
            "borrower",
            "principal_amount",
            "interest_type",
            "interest_value",
            "date_issued",
            "due_date",
            "purpose",
            "notes",
        ]

        widgets = {
            "borrower": forms.Select(
                attrs={"class": "form-select"}
            ),

            "principal_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "interest_type": forms.Select(
                attrs={"class": "form-select"}
            ),

            "interest_value": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "250",
                }
            ),

            "date_issued": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "due_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "purpose": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Purpose of the loan",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional notes",
                }
            ),
        }


class LoanRepaymentForm(forms.ModelForm):
    class Meta:
        model = LoanRepayment
        fields = [
            "amount",
            "payment_date",
            "payment_method",
            "reference",
            "remarks",
        ]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "payment_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "payment_method": forms.Select(
                attrs={"class": "form-select"}
            ),

            "reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Payment reference",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional remarks",
                }
            ),
        }
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
