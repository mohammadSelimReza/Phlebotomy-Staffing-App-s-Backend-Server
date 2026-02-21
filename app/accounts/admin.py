from django.contrib import admin
from .models import CustomerUser,AppointmentModel

class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'gender', 'birth_date', 'role', 'is_active']
    search_fields = ['full_name', 'email', 'phone']
    list_filter = ['role','account_status', 'is_active']

admin.site.register(CustomerUser, CustomerUserAdmin)
admin.site.register(AppointmentModel)