import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

import json
from django.db import transaction
from django.contrib.auth.models import User
from members.models import Family, Contributor, Beneficiary, Payment, SystemSettings


@transaction.atomic
def import_data():
    data = json.load(open("fcs_data.json"))

    users = {
        u.username: u
        for u in User.objects.all()
    }

    user_map = {
        "achanolympia": users["achanolympia"],
        "alarasamson": users["alarasamson"],
        "annakoth": users["annakoth"],
    }

    family_data = next(x for x in data if x["model"] == "members.family")
    family_fields = family_data["fields"]

    family, _ = Family.objects.update_or_create(
        account_number=family_fields["account_number"],
        defaults={
            "name": family_fields["name"],
        },
    )

    contributor_map = {}

    for item in data:
        if item["model"] != "members.contributor":
            continue

        fields = item["fields"]
        username = fields["user"][0]

        contributor, _ = Contributor.objects.update_or_create(
            user=user_map[username],
            defaults={
                "family": family,
                "full_name": fields["full_name"],
                "phone": fields["phone"],
                "email": fields["email"],
                "amount_expected": fields["amount_expected"],
                "is_active": fields["is_active"],
            },
        )

        contributor_map[item["pk"]] = contributor

    for item in data:
        if item["model"] != "members.beneficiary":
            continue

        fields = item["fields"]
        contributor = contributor_map[fields["contributor"]]

        Beneficiary.objects.update_or_create(
            contributor=contributor,
            full_name=fields["full_name"],
            defaults={
                "relationship": fields["relationship"],
                "phone": fields["phone"],
                "is_active": fields["is_active"],
            },
        )

    for item in data:
        if item["model"] != "members.payment":
            continue

        fields = item["fields"]
        contributor = contributor_map[fields["contributor"]]

        Payment.objects.update_or_create(
            receipt_number=fields["receipt_number"],
            defaults={
                "contributor": contributor,
                "amount": fields["amount"],
                "payment_method": fields["payment_method"],
                "payment_date": fields["payment_date"],
                "mpesa_code": None if fields["mpesa_code"] in (None, "Null") else fields["mpesa_code"],
                "status": fields["status"],
                "checkout_request_id": None if fields["checkout_request_id"] in (None, "Null") else fields["checkout_request_id"],
                "phone_number": None if fields["phone_number"] in (None, "Null") else fields["phone_number"],
                "remarks": "" if fields["remarks"] in (None, "Null", "NULL") else fields["remarks"],
            },
        )

    print("FCS DATA IMPORT COMPLETED")
    print("Families:", Family.objects.count())
    print("Contributors:", Contributor.objects.count())
    print("Beneficiaries:", Beneficiary.objects.count())
    print("Payments:", Payment.objects.count())


if __name__ == "__main__":
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    import_data()
