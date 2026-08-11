from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
    "contributors/add/",
    views.add_contributor,
    name="add_contributor"
),
   path(
    "contributors/",
    views.contributor_list,
    name="contributor_list"
),
  path(
    "contributors/edit/<int:pk>/",
    views.edit_contributor,
    name="edit_contributor",
),

path(
    "contributors/delete/<int:pk>/",
    views.delete_contributor,
    name="delete_contributor",
),
 path("families/", views.family_list, name="family_list"),
path("families/add/", views.add_family, name="add_family"),
path("payments/", views.payment_list, name="payment_list"),
path("payments/add/", views.add_payment, name="add_payment"),
path("families/<int:family_id>/delete/", views.delete_family, name="delete_family"),
path(
    "families/<int:family_id>/edit/",
    views.edit_family,
    name="edit_family"),

path(
    "payments/<int:payment_id>/receipt/",
    views.payment_receipt,
    name="payment_receipt",
),
path(
    "payments/edit/<int:payment_id>/",
    views.edit_payment,
    name="edit_payment"
),

path(
    "payments/delete/<int:payment_id>/",
    views.delete_payment,
    name="delete_payment"
),
path(
    "balances/",
    views.balance_report,
    name="balance_report"
),

path(
    "beneficiaries/",
    views.beneficiary_list,
    name="beneficiary_list",
),

path(
    "beneficiaries/add/",
    views.add_beneficiary,
    name="add_beneficiary",
),

path(
    "beneficiaries/edit/<int:pk>/",
    views.edit_beneficiary,
    name="edit_beneficiary",
),

path(
    "beneficiaries/delete/<int:pk>/",
    views.delete_beneficiary,
    name="delete_beneficiary",
),
path(
    "reports/",
    views.reports,
    name="reports",
),
path("login/", views.login_view, name="login"),
path("logout/", views.logout_view, name="logout"),
path(
    "settings/",
    views.settings_view,
    name="settings"
),
]
