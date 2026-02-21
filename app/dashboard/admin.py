from django.contrib import admin
from app.dashboard.models import TermsConditions,PrivacyPolicy
# Register your models here.
admin.site.register(TermsConditions)
admin.site.register(PrivacyPolicy)
