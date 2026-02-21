from django.db import models
from app.accounts.models import CustomerUser
from django.core.validators import MinValueValidator
from django.db import models
from app.accounts.models import CustomerUser
from django.core.validators import MinValueValidator
import cloudinary
import cloudinary.uploader
from cloudinary.models import CloudinaryField


class PhlebotomistProfile(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE, related_name='phlebotomist_profile')

    image = CloudinaryField('image', blank=True, null=True,max_length=20000)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    license_expiry_date = models.DateField(blank=True, null=True)
    years_of_experience = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    speciality = models.CharField(max_length=100, blank=True, null=True)
    license_document_upload = models.FileField(upload_to='phlebotomist_licenses/', blank=True, null=True)  # Document upload
    identification_upload = models.FileField(upload_to='phlebotomist_identifications/', blank=True, null=True)  # Document upload
    work_preferable = models.CharField(max_length=10, choices=[('part_time', 'Part Time'), ('full_time', 'Full Time')], blank=True, null=True)
    service_area = models.CharField(max_length=255, blank=True, null=True)
    weekly_schedule = models.JSONField(default=list, blank=True, null=True)  
    skills = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name}'s Phlebotomist Profile"

    def save(self, *args, **kwargs):
        if self.image and not self.image.startswith("http"):
            upload_result = cloudinary.uploader.upload(self.image)
            self.image = upload_result.get('secure_url')  # Cloudinary image URL
        super().save(*args, **kwargs)
        
        
        
class BusinessOwnerProfile(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE, related_name='business_owner_profile')

    image = models.URLField(max_length=2000, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    business_address = models.CharField(max_length=255, blank=True, null=True)
    contact_person_name = models.CharField(max_length=100, blank=True, null=True)
    business_phone = models.CharField(max_length=20, blank=True, null=True)
    business_license_number = models.CharField(max_length=50, blank=True, null=True)
    business_description = models.TextField(blank=True, null=True)
    business_license_document = models.FileField(upload_to='business_licenses/', blank=True, null=True)  # Document upload
    hourly_pay_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preferred_job_types = models.JSONField(default=list, blank=True, null=True) 
    work_time = models.CharField(max_length=20, choices=[('part_time', 'Part Time'), ('full_time', 'Full Time')], blank=True, null=True)
    weekly_schedule = models.JSONField(default=list, blank=True, null=True)
    digital_sign = models.CharField(max_length=255, blank=True, null=True)
    agree = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.full_name}'s Business Owner Profile"

    def save(self, *args, **kwargs):
        if self.image and not self.image.startswith("http"):
            upload_result = cloudinary.uploader.upload(self.image)
            self.image = upload_result.get('secure_url')  # Cloudinary image URL
        super().save(*args, **kwargs)
