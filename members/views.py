from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
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
from .forms import (
    FamilyForm,
    ContributorForm,
    BeneficiaryForm,
    PaymentForm,
    SettingsForm,
    ContributionObligationForm,
    LoanForm,
    LoanRepaymentForm,
)


# ============================================================
# ACCESS CONTROL
# ============================================================

def superuser_required(view_func):
    """
    Only the administrator/superuser can make changes.
    Normal users can view the system but cannot modify records.
    """
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_superuser
    )(view_func)


# ============================================================
# HOME
# ============================================================

def home(request):
    return render(request, "home.html")


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):
    # ========================================================
    # BASIC COUNTS
    # ========================================================

    total_contributors = Contributor.objects.count()
    total_beneficiaries = Beneficiary.objects.count()
    total_families = Family.objects.count()

    # ========================================================
    # CONTRIBUTIONS
    # ========================================================

    total_expected = (
        Contributor.objects.aggregate(
            total=Sum("amount_expected")
        )["total"]
        or 0
    )

    total_paid = (
        Payment.objects.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    outstanding_balance = total_expected - total_paid

    if total_expected > 0:
        payment_progress = (total_paid / total_expected) * 100
    else:
        payment_progress = 0

    paid_contributors = 0
    owing_contributors = 0

    for contributor in Contributor.objects.all():
        paid = (
            contributor.payments.aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        if paid >= contributor.amount_expected:
            paid_contributors += 1
        else:
            owing_contributors += 1

    # ========================================================
    # RECENT PAYMENTS
    # ========================================================

    recent_payments = Payment.objects.order_by(
        "-payment_date"
    )[:5]

    payment_methods = (
        Payment.objects
        .values("payment_method")
        .annotate(total=Sum("amount"))
    )

    monthly_payments = (
        Payment.objects
        .annotate(month=TruncMonth("payment_date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    # ========================================================
    # CONTRIBUTION OBLIGATIONS
    # ========================================================

    total_obligations = ContributionObligation.objects.count()

    active_obligations = ContributionObligation.objects.filter(
        is_active=True
    ).count()

    inactive_obligations = ContributionObligation.objects.filter(
        is_active=False
    ).count()

    obligation_amount = (
        ContributionObligation.objects.filter(
            is_active=True
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    # ========================================================
    # LOANS
    # ========================================================

    total_loans = Loan.objects.count()

    active_loans = Loan.objects.filter(
        status="ACTIVE"
    ).count()

    paid_loans = Loan.objects.filter(
        status="PAID"
    ).count()

    overdue_loans = Loan.objects.filter(
        status="OVERDUE"
    ).count()

    cancelled_loans = Loan.objects.filter(
        status="CANCELLED"
    ).count()

    total_loan_principal = (
        Loan.objects.aggregate(
            total=Sum("principal_amount")
        )["total"]
        or 0
    )

    total_loan_payable = (
        Loan.objects.aggregate(
            total=Sum("total_payable")
        )["total"]
        or 0
    )

    total_loan_repaid = (
        LoanRepayment.objects.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    loan_outstanding = (
        total_loan_payable - total_loan_repaid
    )

    if loan_outstanding < 0:
        loan_outstanding = 0

    # ========================================================
    # RECENT LOANS
    # ========================================================

    recent_loans = (
        Loan.objects
        .select_related("borrower")
        .order_by("-date_issued")[:5]
    )

    # ========================================================
    # DASHBOARD CONTEXT
    # ========================================================

    context = {
        # Basic
        "total_contributors": total_contributors,
        "total_beneficiaries": total_beneficiaries,
        "total_families": total_families,

        # Contributions
        "total_expected": total_expected,
        "total_paid": total_paid,
        "outstanding_balance": outstanding_balance,
        "payment_progress": payment_progress,
        "paid_contributors": paid_contributors,
        "owing_contributors": owing_contributors,

        # Payments
        "recent_payments": recent_payments,
        "payment_methods": list(payment_methods),
        "monthly_payments": list(monthly_payments),

        # Contribution obligations
        "total_obligations": total_obligations,
        "active_obligations": active_obligations,
        "inactive_obligations": inactive_obligations,
        "obligation_amount": obligation_amount,

        # Loans
        "total_loans": total_loans,
        "active_loans": active_loans,
        "paid_loans": paid_loans,
        "overdue_loans": overdue_loans,
        "cancelled_loans": cancelled_loans,
        "total_loan_principal": total_loan_principal,
        "total_loan_payable": total_loan_payable,
        "total_loan_repaid": total_loan_repaid,
        "loan_outstanding": loan_outstanding,
        "recent_loans": recent_loans,
    }

    return render(
        request,
        "dashboard.html",
        context,
    )

# ============================================================
# CONTRIBUTORS
# ============================================================

@login_required
def contributor_list(request):
    contributors = Contributor.objects.all()

    return render(
        request,
        "contributors/contributor_list.html",
        {"contributors": contributors},
    )


@superuser_required
def add_contributor(request):
    if request.method == "POST":
        form = ContributorForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Contributor added successfully."
            )
            return redirect("contributor_list")
    else:
        form = ContributorForm()

    return render(
        request,
        "contributors/add_contributor.html",
        {"form": form},
    )


@superuser_required
def edit_contributor(request, pk):
    contributor = get_object_or_404(
        Contributor,
        pk=pk,
    )

    if request.method == "POST":
        form = ContributorForm(
            request.POST,
            instance=contributor,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Contributor updated successfully."
            )
            return redirect("contributor_list")
    else:
        form = ContributorForm(
            instance=contributor
        )

    return render(
        request,
        "contributors/add_contributor.html",
        {
            "form": form,
            "edit_mode": True,
            "contributor": contributor,
        },
    )


@superuser_required
def delete_contributor(request, pk):
    contributor = get_object_or_404(
        Contributor,
        pk=pk,
    )

    if request.method == "POST":
        contributor.delete()

        messages.success(
            request,
            "Contributor deleted successfully."
        )

        return redirect("contributor_list")

    return render(
        request,
        "contributors/delete_contributor.html",
        {"contributor": contributor},
    )


# ============================================================
# FAMILIES
# ============================================================

@login_required
def family_list(request):
    families = Family.objects.all()

    return render(
        request,
        "families/family_list.html",
        {"families": families},
    )


@superuser_required
def add_family(request):
    if request.method == "POST":
        form = FamilyForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Family added successfully."
            )

            return redirect("family_list")
    else:
        form = FamilyForm()

    return render(
        request,
        "families/add_family.html",
        {"form": form},
    )


@superuser_required
def edit_family(request, family_id):
    family = get_object_or_404(
        Family,
        id=family_id,
    )

    if request.method == "POST":
        form = FamilyForm(
            request.POST,
            instance=family,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Family updated successfully."
            )

            return redirect("family_list")
    else:
        form = FamilyForm(
            instance=family
        )

    return render(
        request,
        "families/edit_family.html",
        {
            "form": form,
            "family": family,
        },
    )


@superuser_required
def delete_family(request, family_id):
    family = get_object_or_404(
        Family,
        id=family_id,
    )

    if request.method == "POST":
        family.delete()

        messages.success(
            request,
            "Family deleted successfully."
        )

        return redirect("family_list")

    return render(
        request,
        "families/delete_family.html",
        {"family": family},
    )


# ============================================================
# PAYMENTS
# ============================================================

@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by(
        "-payment_date"
    )

    return render(
        request,
        "payments/payment_list.html",
        {"payments": payments},
    )


@superuser_required
def add_payment(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment = form.save()

            # Manual payments are completed immediately.
            payment.status = "Completed"

            if hasattr(payment, "payment_status"):
                payment.payment_status = "Completed"

            payment.save()

            messages.success(
                request,
                "Payment recorded successfully."
            )

            return redirect("payment_list")
    else:
        form = PaymentForm()

    return render(
        request,
        "payments/add_payment.html",
        {"form": form},
    )


@login_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
    )

    return render(
        request,
        "payments/receipt.html",
        {"payment": payment},
    )


@superuser_required
def edit_payment(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
    )

    if request.method == "POST":
        form = PaymentForm(
            request.POST,
            instance=payment,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Payment updated successfully."
            )

            return redirect("payment_list")
    else:
        form = PaymentForm(
            instance=payment
        )

    return render(
        request,
        "payments/add_payment.html",
        {
            "form": form,
            "edit_mode": True,
        },
    )


@superuser_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
    )

    if request.method == "POST":
        payment.delete()

        messages.success(
            request,
            "Payment deleted successfully."
        )

        return redirect("payment_list")

    return render(
        request,
        "payments/delete_payment.html",
        {"payment": payment},
    )


# ============================================================
# BALANCE REPORT
# ============================================================

@login_required
def balance_report(request):
    contributors = Contributor.objects.all()

    for contributor in contributors:
        paid = (
            contributor.payments.aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        contributor.paid_amount = paid

        contributor.balance = (
            contributor.amount_expected - paid
        )

    return render(
        request,
        "contributors/balance_report.html",
        {
            "contributors": contributors
        },
    )


# ============================================================
# REPORTS
# ============================================================

@login_required
def reports(request):
    # ============================================================
    # BASIC COUNTS
    # ============================================================
    contributors = Contributor.objects.count()
    beneficiaries = Beneficiary.objects.count()
    families = Family.objects.count()

    # ============================================================
    # CONTRIBUTION RULE
    # KSh 100 per person, twice per week.
    # Using 4 weeks as one month.
    # ============================================================
    contribution_per_collection = 100
    collections_per_week = 2
    weeks_per_month = 4

    total_paying_people = contributors + beneficiaries

    expected_per_collection = (
        total_paying_people * contribution_per_collection
    )

    expected_per_week = (
        expected_per_collection * collections_per_week
    )

    total_expected = (
        expected_per_week * weeks_per_month
    )

    # ============================================================
    # PAYMENT STATUS TOTALS
    # ============================================================
    completed_payments = (
        Payment.objects
        .filter(status="Completed")
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )

    pending_payments = (
        Payment.objects
        .filter(status="Pending")
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )

    failed_payments = (
        Payment.objects
        .filter(status="Failed")
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )

    # Payment counts
    completed_count = Payment.objects.filter(status="Completed").count()
    pending_count = Payment.objects.filter(status="Pending").count()
    failed_count = Payment.objects.filter(status="Failed").count()

    # ============================================================
    # OUTSTANDING BALANCE
    # Expected contributions minus completed payments
    # ============================================================
    outstanding_balance = total_expected - completed_payments

    if outstanding_balance < 0:
        outstanding_balance = 0

    # ============================================================
    # PAYMENT HISTORY
    # ============================================================
    payments = (
        Payment.objects
        .select_related("contributor")
        .order_by("-payment_date")
    )

    context = {
        "contributors": contributors,
        "beneficiaries": beneficiaries,
        "families": families,

        "total_paying_people": total_paying_people,

        "contribution_per_collection": contribution_per_collection,
        "collections_per_week": collections_per_week,
        "weeks_per_month": weeks_per_month,

        "expected_per_collection": expected_per_collection,
        "expected_per_week": expected_per_week,
        "total_expected": total_expected,

        "completed_payments": completed_payments,
        "pending_payments": pending_payments,
        "failed_payments": failed_payments,

        # Template-compatible names
        "total_paid": completed_payments,
        "total_pending": pending_payments,
        "total_failed": failed_payments,

        "completed_count": completed_count,
        "pending_count": pending_count,
        "failed_count": failed_count,

        "total_collections": completed_payments,
        "outstanding_balance": outstanding_balance,
        "outstanding": outstanding_balance,

        "payments": payments,
    }

    return render(
        request,
        "reports/index.html",
        context,
    )


@login_required
def financial_summary_pdf(request):
    total_contributors = Contributor.objects.count()
    total_beneficiaries = Beneficiary.objects.count()
    total_families = Family.objects.count()

    total_expected = (
        Contributor.objects.aggregate(total=Sum("amount_expected"))["total"] or 0
    )

    total_paid = (
        Payment.objects.aggregate(total=Sum("amount"))["total"] or 0
    )

    outstanding = total_expected - total_paid

    total_loans = Loan.objects.count()

    loan_principal = (
        Loan.objects.aggregate(total=Sum("principal_amount"))["total"] or 0
    )

    loan_repaid = (
        LoanRepayment.objects.aggregate(total=Sum("amount"))["total"] or 0
    )

    loan_outstanding = loan_principal - loan_repaid

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'inline; filename="financial_summary.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 60

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, y, "Family Contribution System")

    y -= 30
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Overall Financial Summary")

    y -= 40
    pdf.setFont("Helvetica", 11)

    summary = [
        ("Total Families", total_families),
        ("Total Contributors", total_contributors),
        ("Total Beneficiaries", total_beneficiaries),
        ("Total Expected Contributions", f"KES {total_expected:,.2f}"),
        ("Total Contributions Paid", f"KES {total_paid:,.2f}"),
        ("Outstanding Contributions", f"KES {outstanding:,.2f}"),
        ("Total Loans", total_loans),
        ("Loan Principal Issued", f"KES {loan_principal:,.2f}"),
        ("Loan Repayments", f"KES {loan_repaid:,.2f}"),
        ("Outstanding Loans", f"KES {loan_outstanding:,.2f}"),
    ]

    for label, value in summary:
        pdf.drawString(60, y, str(label))
        pdf.drawRightString(540, y, str(value))
        y -= 25

    y -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y, "Financial Position")

    y -= 25
    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        60,
        y,
        f"Total money received: KES {total_paid:,.2f}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Contribution balance: KES {outstanding:,.2f}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Loan balance outstanding: KES {loan_outstanding:,.2f}"
    )

    y -= 40

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(
        60,
        y,
        "Generated by Family Contribution System"
    )

    pdf.save()

    return response

# ============================================================
# ============================================================

@superuser_required


# ============================================================
# ============================================================



# ============================================================
# BENEFICIARIES
# ============================================================

@login_required
def beneficiary_list(request):
    beneficiaries = Beneficiary.objects.all()

    return render(
        request,
        "beneficiaries/list.html",
        {
            "beneficiaries": beneficiaries
        },
    )


@superuser_required
def add_beneficiary(request):
    if request.method == "POST":
        form = BeneficiaryForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Beneficiary added successfully."
            )

            return redirect(
                "beneficiary_list"
            )
    else:
        form = BeneficiaryForm()

    return render(
        request,
        "beneficiaries/add.html",
        {
            "form": form
        },
    )


@superuser_required
def edit_beneficiary(request, pk):
    beneficiary = get_object_or_404(
        Beneficiary,
        pk=pk,
    )

    if request.method == "POST":
        form = BeneficiaryForm(
            request.POST,
            instance=beneficiary,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Beneficiary updated successfully."
            )

            return redirect(
                "beneficiary_list"
            )
    else:
        form = BeneficiaryForm(
            instance=beneficiary
        )

    return render(
        request,
        "beneficiaries/add.html",
        {
            "form": form,
            "edit_mode": True,
        },
    )


@superuser_required
def delete_beneficiary(request, pk):
    beneficiary = get_object_or_404(
        Beneficiary,
        pk=pk,
    )

    if request.method == "POST":
        beneficiary.delete()

        messages.success(
            request,
            "Beneficiary deleted successfully."
        )

        return redirect(
            "beneficiary_list"
        )

    return render(
        request,
        "beneficiaries/delete.html",
        {
            "beneficiary": beneficiary
        },
    )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(
        request,
        data=request.POST or None,
    )

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()

            login(request, user)

            return redirect("dashboard")

    return render(
        request,
        "registration/login.html",
        {
            "form": form
        },
    )


# ============================================================
# LOGOUT
# ============================================================

@login_required
def logout_view(request):
    logout(request)

    return redirect("login")


# ============================================================
# SYSTEM SETTINGS
# ============================================================

@superuser_required
def settings_view(request):
    settings_obj, created = (
        SystemSettings.objects.get_or_create(
            id=1
        )
    )

    if request.method == "POST":
        form = SettingsForm(
            request.POST,
            instance=settings_obj,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "System settings updated successfully."
            )

            return redirect("settings")
    else:
        form = SettingsForm(
            instance=settings_obj
        )

    return render(
        request,
        "settings.html",
        {
            "form": form
        },
    )
# ============================================================
# CONTRIBUTION OBLIGATIONS
# ============================================================

@login_required
def contribution_obligation_list(request):
    obligations = (
        ContributionObligation.objects
        .select_related("contributor", "beneficiary")
        .order_by("-is_active", "contributor__full_name")
    )

    return render(
        request,
        "contributions/obligation_list.html",
        {
            "obligations": obligations,
        },
    )


@superuser_required
def add_contribution_obligation(request):
    if request.method == "POST":
        form = ContributionObligationForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Contribution obligation added successfully."
            )

            return redirect("contribution_obligation_list")
    else:
        form = ContributionObligationForm()

    return render(
        request,
        "contributions/add_obligation.html",
        {
            "form": form,
        },
    )


@superuser_required
def edit_contribution_obligation(request, pk):
    obligation = get_object_or_404(
        ContributionObligation,
        pk=pk,
    )

    if request.method == "POST":
        form = ContributionObligationForm(
            request.POST,
            instance=obligation,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Contribution obligation updated successfully."
            )

            return redirect("contribution_obligation_list")
    else:
        form = ContributionObligationForm(
            instance=obligation
        )

    return render(
        request,
        "contributions/add_obligation.html",
        {
            "form": form,
            "edit_mode": True,
            "obligation": obligation,
        },
    )


@superuser_required
def delete_contribution_obligation(request, pk):
    obligation = get_object_or_404(
        ContributionObligation,
        pk=pk,
    )

    if request.method == "POST":
        obligation.delete()

        messages.success(
            request,
            "Contribution obligation deleted successfully."
        )

        return redirect("contribution_obligation_list")

    return render(
        request,
        "contributions/delete_obligation.html",
        {
            "obligation": obligation,
        },
    )
# ============================================================
# LOANS
# ============================================================

@login_required
def loan_list(request):
    loans = (
        Loan.objects
        .select_related("borrower")
        .order_by("-date_issued", "-created_at")
    )

    return render(
        request,
        "loans/loan_list.html",
        {
            "loans": loans,
        },
    )


@login_required
def loan_detail(request, pk):
    loan = get_object_or_404(
        Loan.objects.select_related("borrower"),
        pk=pk,
    )

    repayments = loan.repayments.order_by(
        "-payment_date"
    )

    return render(
        request,
        "loans/loan_detail.html",
        {
            "loan": loan,
            "repayments": repayments,
        },
    )


@superuser_required
def add_loan(request):
    if request.method == "POST":
        form = LoanForm(request.POST)

        if form.is_valid():
            loan = form.save()

            messages.success(
                request,
                "Loan recorded successfully."
            )

            return redirect(
                "loan_detail",
                pk=loan.pk,
            )
    else:
        form = LoanForm()

    return render(
        request,
        "loans/add_loan.html",
        {
            "form": form,
        },
    )


@superuser_required
def add_loan_repayment(request, loan_id):
    loan = get_object_or_404(
        Loan,
        pk=loan_id,
    )

    if request.method == "POST":
        form = LoanRepaymentForm(request.POST)

        if form.is_valid():
            repayment = form.save(commit=False)
            repayment.loan = loan
            repayment.save()

            messages.success(
                request,
                "Loan repayment recorded successfully."
            )

            return redirect(
                "loan_detail",
                pk=loan.pk,
            )
    else:
        form = LoanRepaymentForm()

    return render(
        request,
        "loans/add_repayment.html",
        {
            "form": form,
            "loan": loan,
        },
    )
