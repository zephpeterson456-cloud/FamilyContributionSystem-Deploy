from django.shortcuts import render
from .forms import PaymentForm
from .forms import BeneficiaryForm
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncMonth
from .forms import SettingsForm
from .models import SystemSettings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Family
from django.contrib.admin.views.decorators import staff_member_required
def home(request):
    return render(request, "home.html")
from django.shortcuts import render
from .models import Family , Contributor, Beneficiary, Payment
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .forms import FamilyForm
@login_required
def dashboard(request):
    total_contributors = Contributor.objects.count()
    total_beneficiaries = Beneficiary.objects.count()
    total_families = Family.objects.count()

    total_expected = Contributor.objects.aggregate(
        total=Sum("amount_expected")
    )["total"] or 0

    total_paid = Payment.objects.aggregate(
        total=Sum("amount")
    )["total"] or 0

    outstanding_balance = total_expected - total_paid

    paid_contributors = 0
    owing_contributors = 0

    for contributor in Contributor.objects.all():

        paid = contributor.payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        if paid >= contributor.amount_expected:
            paid_contributors += 1
        else:
            owing_contributors += 1

    recent_payments = Payment.objects.order_by(
        "-payment_date"
    )[:5]

    payment_methods = Payment.objects.values(
        "payment_method"
    ).annotate(
        total=Sum("amount")
    )

    monthly_payments = Payment.objects.annotate(
        month=TruncMonth("payment_date")
    ).values(
        "month"
    ).annotate(
        total=Sum("amount")
    ).order_by("month")
    context = {
        "total_contributors": total_contributors,
        "total_beneficiaries": total_beneficiaries,
        "total_families": total_families,

        "total_expected": total_expected,
        "total_paid": total_paid,
        "outstanding_balance": outstanding_balance,

        "paid_contributors": paid_contributors,
        "owing_contributors": owing_contributors,

        "recent_payments": recent_payments,
        "payment_methods": list(payment_methods),
        "monthly_payments": list(monthly_payments),
    }
    return render(request,"dashboard.html",context)
from django.shortcuts import render, redirect
from .forms import ContributorForm
@login_required
def add_contributor(request):
    if request.method == "POST":
        form = ContributorForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("contributor_list")
    else:
        form = ContributorForm()

    return render(
        request,
        "contributors/add_contributor.html",
        {"form": form}
    )


@login_required
def contributor_list(request):
    contributors = Contributor.objects.all()

    return render(
        request,
        "contributors/contributor_list.html",
        {"contributors": contributors}
    )


@login_required
def edit_contributor(request, pk):
    contributor = get_object_or_404(Contributor, pk=pk)

    if request.method == "POST":
        form = ContributorForm(
            request.POST,
            instance=contributor
        )

        if form.is_valid():
            form.save()
            return redirect("contributor_list")
    else:
        form = ContributorForm(instance=contributor)

    return render(
        request,
        "contributors/add_contributor.html",
        {
            "form": form,
            "edit_mode": True,
            "contributor": contributor,
        }
    )


@login_required
def delete_contributor(request, pk):
    contributor = get_object_or_404(Contributor, pk=pk)

    if request.method == "POST":
        contributor.delete()
        return redirect("contributor_list")

    return render(
        request,
        "contributors/delete_contributor.html",
        {"contributor": contributor}
    )



from .forms import ContributorForm, FamilyForm
def family_list(request):
    families = Family.objects.all()

    return render(
        request,
        "families/family_list.html",
        {"families": families}
    )

def delete_family(request, family_id):
    family = get_object_or_404(Family, id=family_id)

    if request.method == "POST":
        family.delete()
        messages.success(request, "Family deleted successfully.")
        return redirect("family_list")

    return render(
        request,
        "families/delete_family.html",
        {"family": family}
    )
def edit_family(request, family_id):
    family = get_object_or_404(Family, id=family_id)

    if request.method == "POST":
        form = FamilyForm(request.POST, instance=family)

        if form.is_valid():
            form.save()
            messages.success(request, "Family updated successfully.")
            return redirect("family_list")
    else:
        form = FamilyForm(instance=family)

    return render(
        request,
        "families/edit_family.html",
        {"form": form, "family": family}
    )
@login_required
def add_family(request):

    if request.method == "POST":
        form = FamilyForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("family_list")

    else:
        form = FamilyForm()

    return render(
        request,
        "families/add_family.html",
        {"form": form}
    )
@login_required
def delete_family(request, family_id):
    if request.method == "POST":
        family = get_object_or_404(Family, id=family_id)
        family.delete()
        messages.success(request, "Family deleted successfully.")
    return redirect("family_list")	
@login_required
def add_payment(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment = form.save()

            # Manual payments are completed immediately
            payment.status = "Completed"
            payment.payment_status = "Completed"
            payment.save()

            return redirect("payment_list")

    else:
        form = PaymentForm()

    return render(
        request,
        "payments/add_payment.html",
        {"form": form}
    )
@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by("-payment_date")

    return render(
        request,
        "payments/payment_list.html",
        {"payments": payments}
    )
@login_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    return render(
        request,
        "payments/receipt.html",
        {"payment": payment}
    )
@login_required
def edit_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)

        if form.is_valid():
            form.save()
            messages.success(request, "Payment updated successfully.")
            return redirect("payment_list")
    else:
        form = PaymentForm(instance=payment)

    return render(
        request,
        "payments/add_payment.html",
        {
            "form": form,
            "edit_mode": True,
        }
    )


@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == "POST":
        payment.delete()
        messages.success(request, "Payment deleted successfully.")
        return redirect("payment_list")

    return render(
        request,
        "payments/delete_payment.html",
        {
            "payment": payment,
        }
    )
@login_required
def balance_report(request):

    contributors = Contributor.objects.all()

    for contributor in contributors:

        paid = contributor.payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        contributor.paid_amount = paid
        contributor.balance = (
            contributor.amount_expected - paid
        )

    return render(
        request,
        "contributors/balance_report.html",
        {
            "contributors": contributors
        }
    )
@login_required
def reports(request):
    contributors = Contributor.objects.all()

    for contributor in contributors:
        paid = contributor.payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        contributor.paid_amount = paid
        contributor.balance = contributor.amount_expected - paid

    return render(
        request,
        "contributors/balance_report.html",
        {
            "contributors": contributors
        }
    )
from .mpesa import stk_push
from .models import Payment, Contributor
from django.http import JsonResponse

@login_required
def initiate_mpesa(request):
    if request.method == "POST":
        contributor_id = request.POST.get("contributor")
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        contributor = Contributor.objects.get(id=contributor_id)

        payment = Payment.objects.create(
            contributor=contributor,
            amount=amount,
            payment_method="M-Pesa",
            phone_number=phone,
            status="Pending",
        )

        response = stk_push(
            phone=phone,
            amount=int(amount),
            account_reference=f"FCS{payment.id}",
            transaction_desc="Family Contribution",
        )

        if response.get("ResponseCode") == "0":
            payment.checkout_request_id = response.get("CheckoutRequestID")
            payment.save()

        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"}, status=400)

from django.http import JsonResponse

import json
from django.http import JsonResponse

def mpesa_callback(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    try:
        callback = data["Body"]["stkCallback"]

        checkout_request_id = callback["CheckoutRequestID"]
        result_code = callback["ResultCode"]

        payment = Payment.objects.get(
            checkout_request_id=checkout_request_id
        )

        if result_code == 0:
            payment.status = "Completed"

            for item in callback.get("CallbackMetadata", {}).get("Item", []):
                if item["Name"] == "MpesaReceiptNumber":
                    payment.mpesa_code = item["Value"]

            payment.save()

        else:
            payment.status = "Failed"
            payment.save()

    except Exception as e:
        print("Callback Error:", e)

    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })
@login_required
def add_beneficiary(request):
    if request.method == "POST":
        form = BeneficiaryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("beneficiary_list")
    else:
        form = BeneficiaryForm()

    return render(
        request,
        "beneficiaries/add.html",
        {
            "form": form
        }
    )


@login_required
def beneficiary_list(request):
    beneficiaries = Beneficiary.objects.all()

    return render(
        request,
        "beneficiaries/list.html",
        {
            "beneficiaries": beneficiaries
        }
    )


@login_required
def edit_beneficiary(request, pk):
    beneficiary = get_object_or_404(
        Beneficiary,
        pk=pk
    )

    if request.method == "POST":
        form = BeneficiaryForm(
            request.POST,
            instance=beneficiary
        )

        if form.is_valid():
            form.save()
            return redirect("beneficiary_list")
    else:
        form = BeneficiaryForm(
            instance=beneficiary
        )

    return render(
        request,
        "beneficiaries/add.html",
        {
            "form": form
        }
    )


@login_required
def delete_beneficiary(request, pk):
    beneficiary = get_object_or_404(
        Beneficiary,
        pk=pk
    )

    if request.method == "POST":
        beneficiary.delete()
        return redirect("beneficiary_list")

    return render(
        request,
        "beneficiaries/delete.html",
        {
            "beneficiary": beneficiary
        }
    )
@login_required
def reports(request):
    contributors = Contributor.objects.count()
    beneficiaries = Beneficiary.objects.count()
    families = Family.objects.count()

    total_collections = Payment.objects.aggregate(
        total=Sum("amount")
    )["total"] or 0

    payments = Payment.objects.select_related(
        "contributor"
    ).order_by("-payment_date")[:20]

    context = {
        "contributors": contributors,
        "beneficiaries": beneficiaries,
        "families": families,
        "total_collections": total_collections,
        "payments": payments,
    }

    return render(
        request,
        "reports/index.html",
        context,
    )
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")

    return render(
        request,
        "registration/login.html",
        {"form": form},
    )


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def settings_view(request):

    settings_obj, created = SystemSettings.objects.get_or_create(
        id=1
    )

    if request.method == "POST":

        form = SettingsForm(
            request.POST,
            instance=settings_obj
        )

        if form.is_valid():
            form.save()
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
        }
    )
