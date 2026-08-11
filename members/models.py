from django.db import models
from django.utils import timezone
from .utils  import generate_receipt

class Family(models.Model):
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Contributor(models.Model):
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
