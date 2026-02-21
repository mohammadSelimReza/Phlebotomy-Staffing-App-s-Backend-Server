from django.contrib import admin
from django.db.models import Count

from .models import Job,TempAssignedJob,AcceptedAssignedJob,CompletedAssignedJob
# Register your models here.

class CompletedAssignedJobAdmin(admin.ModelAdmin):
    list_display = ('job', 'completed_by', 'assigned_by', 'completed_on', 'is_active', 'completion_count')
    list_filter = ('completed_by__email',)  # Filter by email of the user (completed_by)
    search_fields = ('completed_by__email', 'job__title')  # Allow searching by user email and job title

    # Annotate completion count for each user
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(completion_count=Count('completed_by'))
        return queryset

    # Add the completion_count to the list display
    def completion_count(self, obj):
        return obj.completion_count
    completion_count.admin_order_field = 'completion_count'  # Make it sortable
    completion_count.short_description = 'Completed Jobs Count'

    # Optional: You can also add ordering to make it easier to sort by a particular field
    ordering = ('-completed_on',)  # Order by completed_on in descending order

admin.site.register(CompletedAssignedJob, CompletedAssignedJobAdmin)

admin.site.register(Job)
admin.site.register(TempAssignedJob)
admin.site.register(AcceptedAssignedJob)
