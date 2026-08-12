from django.contrib import admin
from .models import (
    Family,
    Contributor,
    Beneficiary,
    Payment,
    SystemSettings,
    ContributionObligation,
    Loan,
    LoanRepayment,
)


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("name", "account_number", "created_at")
    search_fields = ("name", "account_number")


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "family",
        "amount_expected",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_active", "family")
    search_fields = ("full_name", "phone", "email")


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "contributor",
        "relationship",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("full_name", "phone")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "contributor",
        "amount",
        "payment_method",
        "status",
        "payment_date",
        "mpesa_code",
    )
    list_filter = ("status", "payment_method")
    search_fields = (
        "receipt_number",
        "contributor__full_name",
        "mpesa_code",
    )


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ("organization_name", "monthly_contribution", "created_at")


@admin.register(ContributionObligation)
class ContributionObligationAdmin(admin.ModelAdmin):
    list_display = (
        "contributor",
        "beneficiary",
        "amount",
        "frequency",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("frequency", "is_active")
    search_fields = (
        "contributor__full_name",
        "beneficiary__full_name",
    )


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "borrower",
        "principal_amount",
        "interest_type",
        "interest_value",
        "interest_amount",
        "total_payable",
        "amount_repaid",
        "status",
        "date_issued",
        "due_date",
    )
    list_filter = ("status", "interest_type")
    search_fields = ("borrower__full_name",)


@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = (
        "loan",
        "amount",
        "payment_date",
        "payment_method",
        "reference",
    )
    list_filter = ("payment_method",)
    search_fields = (
        "loan__borrower__full_name",
        "reference",
    )
