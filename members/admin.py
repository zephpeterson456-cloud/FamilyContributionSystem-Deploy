from django.contrib import admin
from .models import Contributor,Beneficiary,Payment

admin.site.register(Contributor)
admin.site.register(Beneficiary)
admin.site.register(Payment)
