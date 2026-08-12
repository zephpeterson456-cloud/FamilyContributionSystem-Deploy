from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils  import generate_receipt

class Family(models.Model):
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Contributor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contributor_profile",
    )

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="contributors"
    )

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)

    amount_expected = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(default=True)

    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Beneficiary(models.Model):
    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.CASCADE,
        related_name="beneficiaries"
    )

    full_name = models.CharField(max_length=100)

    relationship = models.CharField(max_length=50)

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.full_name
class Payment(models.Model):

    METHODS = [
        ("Cash", "Cash"),
        ("M-Pesa", "M-Pesa"),
        ("Bank", "Bank"),
    ]

    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=METHODS
    )

    payment_date = models.DateTimeField(
        default=timezone.now
    )

    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        default=generate_receipt
    )

    mpesa_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
  
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Completed", "Completed"),
            ("Failed", "Failed"),
        ],
        default="Pending",
    )

    checkout_request_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.contributor.full_name} - {self.amount}"
class SystemSettings(models.Model):
    organization_name = models.CharField(
        max_length=100,
        default="Family Contribution System"
    )

    monthly_contribution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    mpesa_shortcode = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    mpesa_consumer_key = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    mpesa_consumer_secret = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    mpesa_passkey = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.organization_name
class ContributionObligation(models.Model):
    FREQUENCIES = [
        ("TWICE_WEEKLY", "Twice a week"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
    ]

    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.CASCADE,
        related_name="obligations"
    )

    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contribution_obligations"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount paid for this person each contribution."
    )

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCIES,
        default="TWICE_WEEKLY"
    )

    start_date = models.DateField(
        default=timezone.now
    )

    end_date = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        if self.beneficiary:
            recipient = self.beneficiary.full_name
        else:
            recipient = f"{self.contributor.full_name} (Self)"

        return f"{self.contributor.full_name} → {recipient}: KES {self.amount}"


class Loan(models.Model):
    INTEREST_TYPES = [
        ("FIXED", "Fixed amount"),
        ("PERCENTAGE", "Percentage"),
    ]

    STATUSES = [
        ("ACTIVE", "Active"),
        ("PAID", "Paid"),
        ("OVERDUE", "Overdue"),
        ("CANCELLED", "Cancelled"),
    ]

    borrower = models.ForeignKey(
        Contributor,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    principal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    interest_type = models.CharField(
        max_length=20,
        choices=INTEREST_TYPES,
        default="FIXED"
    )

    interest_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=250
    )

    interest_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=250
    )

    total_payable = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    amount_repaid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    date_issued = models.DateField(
        default=timezone.now
    )

    due_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default="ACTIVE"
    )

    purpose = models.TextField(
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def balance(self):
        return max(
            self.total_payable - self.amount_repaid,
            0
        )

    def calculate_interest(self):
        if self.interest_type == "FIXED":
            return self.interest_value

        return (
            self.principal_amount *
            self.interest_value /
            100
        )

    def save(self, *args, **kwargs):
        self.interest_amount = self.calculate_interest()

        self.total_payable = (
            self.principal_amount +
            self.interest_amount
        )

        if self.amount_repaid >= self.total_payable:
            self.status = "PAID"

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.borrower.full_name} - "
            f"KES {self.principal_amount}"
        )


class LoanRepayment(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="repayments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateTimeField(
        default=timezone.now
    )

    payment_method = models.CharField(
        max_length=20,
        choices=Payment.METHODS,
        default="Cash"
    )

    reference = models.CharField(
        max_length=50,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.loan.borrower.full_name} - "
            f"KES {self.amount}"
        )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:
            total_repaid = sum(
                repayment.amount
                for repayment in self.loan.repayments.all()
            )

            self.loan.amount_repaid = total_repaid
            self.loan.save()
