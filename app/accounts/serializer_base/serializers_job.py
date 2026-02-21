from rest_framework import serializers
from app.business_owner.models import AcceptedAssignedJob
from django.utils import timezone
from django.db.models import Sum


class PhlebotomistJobHistorySerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title')
    job_creator_name = serializers.CharField(source='job.created_by.full_name')
    start_date = serializers.DateField(source='job.date')
    start_time = serializers.TimeField(source='job.start_time')
    end_time = serializers.TimeField(source='job.end_time')
    pay_rate = serializers.DecimalField(source='job.pay_rate', max_digits=10, decimal_places=2)
    total_payment = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_hour = serializers.CharField(source='job.total_working_hour')

    class Meta:
        model = AcceptedAssignedJob
        fields = ['id','job_title', 'job_creator_name', 'start_date', 'start_time', 'end_time', 'pay_rate', 'total_payment', 'total_hour']

    def to_representation(self, instance):
        """
        Override the to_representation method to calculate and return:
        - Total earnings for the current month
        - Total completed jobs for the current month
        """
        data = super().to_representation(instance)

        # Get the current month and year
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Total Earnings (this month)
        total_earnings = AcceptedAssignedJob.objects.filter(
            assigned_to=instance.assigned_to,
            completed=True,  # Ensure the job is completed
            accepted_on__year=current_year,
            accepted_on__month=current_month
        ).aggregate(Sum('total_payment'))['total_payment__sum'] or 0.00

        # Total Completed Jobs (this month)
        total_completed_jobs = AcceptedAssignedJob.objects.filter(
            assigned_to=instance.assigned_to,
            completed=True,  # Ensure the job is completed
            accepted_on__year=current_year,
            accepted_on__month=current_month
        ).count()

        # Add additional fields for the summary
        data['total_earnings'] = total_earnings
        data['total_completed_jobs'] = total_completed_jobs
        return data