from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth.models import AbstractBaseUser
from app.accounts.manager import CustomUserManager
from datetime import datetime, timedelta
from django.utils import timezone
import cloudinary
import cloudinary.uploader
from cloudinary.models import CloudinaryField
# Create your models here.

class CustomerUser(AbstractBaseUser):
    ADMIN = 'admin'
    USER = 'user'
    PHLEBOTOMIST = 'phlebotomist'
    BUSINESS_OWNER = 'business_owner'
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    ROLE_CHOICES = [
        (ADMIN,'admin'),
        (USER,'user'),
        (PHLEBOTOMIST,'phlebotomist'),
        (BUSINESS_OWNER,'business_owner')
    ]
    
    STATUS = [
        (PENDING,'pending'),
        (APPROVED,'approved'),
        (REJECTED,'rejected')
    ]
    
    #
    user_id = ShortUUIDField(length=6,max_length=6,alphabet="0123456789",primary_key=True)
    username = models.CharField(max_length=20,null=True,blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20,blank=True,null=True)
    gender = models.CharField(max_length=10,choices=[('Male','male'),('Female','female')])
    birth_date = models.DateField()
    #
    role = models.CharField(max_length=20,choices=ROLE_CHOICES)
    account_status = models.CharField(max_length=30, choices=STATUS, default=PENDING,null=True)
    #
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    #
    
    
    #
    
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name','phone','gender','birth_date','role']
    
    def __str__(self):
        return f"Account of {self.email}"
    
    def save(self, *args, **kwargs):
        if not self.username or self.username == " ":
            # Safely split email to create a username
            email_user_name, _ = self.email.split("@")
            self.username = email_user_name
        if self.role in [self.ADMIN, self.USER]:
            self.account_status = self.APPROVED
        
        super().save(*args, **kwargs)
        
    def has_perm(self, perm, obj=None):
        return self.is_admin or self.is_staff

    def has_module_perms(self, app_label):
        return self.is_admin or self.is_staff
      
class AppointmentModel(models.Model):
    appointment_id = ShortUUIDField(length=6, max_length=6, alphabet="0123456789", primary_key=True)

    user = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL,null=True, related_name="appointments")

    test_package = models.ForeignKey('business_owner.Job',on_delete=models.CASCADE,related_name='appointment_job')

    start_date = models.DateField()
    start_date_start_time = models.TimeField()
    start_date_end_time = models.TimeField()
    end_date = models.DateField()
    end_date_start_time = models.TimeField()
    end_date_end_time = models.TimeField()

    hospital = models.CharField(max_length=255,blank=True,null=True)
    location = models.TextField()

    current_medication = models.TextField(blank=True, null=True)
    prescription = CloudinaryField('prescription', blank=True, null=True, max_length=20000)
    known_allergies = models.TextField(blank=True, null=True)
    medical_conditions = models.JSONField(default=list)

    special_request = models.CharField(max_length=1024, blank=True, null=True)
    email_notification_enable = models.BooleanField(default=False)
    terms_and_condition_agreement = models.BooleanField(default=False)
    agreement = models.BooleanField(default=False)
    #
    initial_fee = models.DecimalField(default=0,max_digits=6,decimal_places=2,null=True,blank=True)
    service_fee = models.DecimalField(default=0,max_digits=6,decimal_places=2,null=True,blank=True)
    tax_fee = models.DecimalField(default=0,max_digits=6,decimal_places=2,null=True,blank=True)
    total = models.DecimalField(default=0,max_digits=6,decimal_places=2,null=True,blank=True)
    # billing address
    street_address = models.CharField(max_length=255,blank=True,null=True)
    city = models.CharField(max_length=255,blank=True,null=True)
    state = models.CharField(max_length=255,blank=True,null=True)
    zip_code = models.PositiveIntegerField(default=0,blank=True,null=True)
    payment_status = models.BooleanField(default=False,null=True)
    
    #
    assigned = models.ForeignKey(CustomerUser,on_delete=models.SET_NULL,null=True)
    #
    
    def save(self, *args, **kwargs):
        serviceFee = self.service_fee or 0
        taxFee = self.tax_fee or 0
        self.total = (self.initial_fee or 0) + serviceFee + taxFee
        super().save(*args, **kwargs)
    
    #
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment {self.appointment_id} for {self.user.full_name}"
         
        
class PasswordResetOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    
class ReportUserModel(models.Model):
    LOW = "low"
    MEDIUM = "medium"
    HIGH =  "high"
    
    FLAG_CHOICES = (
        (LOW, "low"),
        (MEDIUM, "medium"),
        (HIGH, "high")
    )
    PENDING = "pending"
    SOLVED = "solved"
    CLOSED = "closed"

    CASE_STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (SOLVED, 'Solved'),
        (CLOSED, 'Closed'),
    )
    reported_id = ShortUUIDField(length=6, max_length=6, alphabet="0123456789", primary_key=True, db_index=True)
    

    reported_to = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, related_name="reports_received")
    reported_reason = models.CharField(max_length=255)
    additional_details = models.TextField(null=True, blank=True)
    case_status = models.CharField(choices=CASE_STATUS_CHOICES, default=PENDING, max_length=20)
    ai_flag_title = models.CharField(max_length=255, null=True, blank=True)
    ai_flagged_responsed = models.BooleanField(default=False)
    ai_flag = models.CharField(max_length=255,choices=FLAG_CHOICES, null=True)

    reported_by = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name="reports_made")
    reported_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"Report {self.reported_id} by {self.reported_by.full_name} to {self.reported_to.full_name}"


class NotificationModel(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=1024)
    info = models.TextField()
    is_read = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name}: {self.title}"

class ActivityLog(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=1024)
    info = models.TextField()
    log_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name}: {self.title}"

    