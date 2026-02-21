from django.db import models
from app.accounts.models import CustomerUser
from shortuuid.django_fields import ShortUUIDField
from datetime import datetime
from django.utils import timezone

class Job(models.Model):
    URGENT = 'urgent'
    FULL_DAY = 'full_day'
    PART_TIME = 'part_time'

    JOB_TYPE_CHOICES = [
        (URGENT, 'Urgent'),
        (FULL_DAY, 'Full Day'),
        (PART_TIME, 'Part Time')
    ]

    HOURLY = 'hourly'
    FLAT_RATE = 'flat_rate'

    PAY_TYPE_CHOICES = [
        (HOURLY, 'Hourly'),
        (FLAT_RATE, 'Flat Rate')
    ]

    # Add active status options
    APPROVED = 'approved'
    PENDING = 'pending'
    REJECTED = 'rejected'
    
    ACTIVE_STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (PENDING, 'Pending'),
        (REJECTED, 'Rejected')
    ]

    title = models.CharField(max_length=255)
    id = ShortUUIDField(length=6, max_length=6, alphabet="0123456789", primary_key=True)
    profession_type = models.CharField(max_length=255)
    job_info = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_working_hour = models.CharField(max_length=255,null=True, blank=True)
    pay_type = models.CharField(max_length=10, choices=PAY_TYPE_CHOICES)
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2)
    job_types = models.CharField(max_length=10, choices=JOB_TYPE_CHOICES)
    
    # Add the active_status field
    active_status = models.CharField(max_length=20, choices=ACTIVE_STATUS_CHOICES, default=PENDING)

    assigned = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')

    completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_jobs')
    
    created_by = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='created_jobs')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        delta = datetime.combine(self.date, self.end_time) - datetime.combine(self.date, self.start_time)
        self.total_working_hour = str(delta)
        super().save(*args, **kwargs)
    
        
        
class TempAssignedJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='temp_assignments')
    assigned_to = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='temp_assigned_jobs')
    assigned_by = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='temp_assigned_by')
    assignment_start_time = models.DateTimeField()
    assignment_end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('assigned', 'Assigned'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='assigned')
    is_accepted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Temporary Assignment for Job: {self.job.title} (Assigned to: {self.assigned_to.full_name})"

    def save(self, *args, **kwargs):
        # Ensure that assignment_end_time is timezone-aware
        if self.assignment_end_time and timezone.is_naive(self.assignment_end_time):
            self.assignment_end_time = timezone.make_aware(self.assignment_end_time, timezone.get_current_timezone())
        
        # Automatically set the status to 'completed' if assignment_end_time has passed
        if self.assignment_end_time <= timezone.now():
            self.status = 'completed'

        super().save(*args, **kwargs)

class RequestForJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='request_job')
    requested_by = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_request_by')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('rejected', 'Rejected')], default='pending')
    is_active = models.BooleanField(default=True)

    requested_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class AcceptedAssignedJob(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='accepted_assignments'
    )
    assigned_to = models.ForeignKey(
        CustomerUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_jobs'
    )
    assigned_by = models.ForeignKey(
        CustomerUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs_accepted_by_worker'
    )

    accepted_on = models.DateTimeField(auto_now_add=True, null=True)
    completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add this line

    def __str__(self):
        return f"Accepted Job: {self.job.title} by {self.assigned_to}"


    def save(self, *args, **kwargs):
        from decimal import Decimal
        if self.completed:
            # Split the total_working_hour into hours and minutes
            total_hours = self.job.total_working_hour.split(":")
            hours = int(total_hours[0])
            minutes = int(total_hours[1])

            # Convert hours and minutes to a Decimal value
            total_hours_decimal = Decimal(hours) + Decimal(minutes) / Decimal(60)

            # Calculate total payment using the Decimal value for hours worked
            total_payment = self.job.pay_rate * total_hours_decimal
            self.total_payment = total_payment

        # Save the object
        super().save(*args, **kwargs)

    
class CompletedAssignedJob(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='completed_assignments'
    )
    completed_by = models.ForeignKey(
        CustomerUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_assigned_jobs'
    )
    assigned_by = models.ForeignKey(
        CustomerUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs_marked_completed_by'
    )
    payment_status = models.BooleanField(default=False)
    completed_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Completed Job: {self.job.title} by {self.completed_by}"