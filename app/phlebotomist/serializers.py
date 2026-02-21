from rest_framework import serializers
from app.accounts.models import CustomerUser
from app.accounts.models_profile import PhlebotomistProfile
from app.business_owner.models import Job,AcceptedAssignedJob

class PhlebotomistListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    years_of_experience = serializers.SerializerMethodField()
    class Meta:
        model = CustomerUser
        fields = ['user_id', 'image', 'full_name', 'years_of_experience','email']

    def get_image(self, obj):
        phlebotomist_profile = obj.phlebotomist_profile
        return phlebotomist_profile.image if phlebotomist_profile else None

    def get_years_of_experience(self,obj):
        return obj.phlebotomist_profile.years_of_experience or 0
    
    
class PhlebotomistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhlebotomistProfile
        fields = [
            'image', 'license_number', 'license_expiry_date', 'years_of_experience', 
            'speciality', 'license_document_upload', 'identification_upload', 
            'work_preferable', 'service_area', 'weekly_schedule', 'skills'
        ]

class PhlebotomistDetailSerializer(serializers.ModelSerializer):
    phlebotomist_profile = PhlebotomistProfileSerializer()

    class Meta:
        model = CustomerUser
        fields = [
            'user_id', 'full_name', 'email', 'phone', 'gender', 'birth_date', 'role',
            'phlebotomist_profile'
        ]

    def get_image(self, obj):
        # Access image from the related PhlebotomistProfile via the nested serializer
        return obj.phlebotomist_profile.image if obj.phlebotomist_profile else None
    
    
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'profession_type', 'job_info', 'location', 'date', 'start_time', 'end_time', 'total_working_hour', 'pay_type', 'pay_rate', 'job_types', 'active_status']

class AcceptedAssignedJobSerializer(serializers.ModelSerializer):
    job = JobSerializer()  # Include the job details using JobSerializer

    class Meta:
        model = AcceptedAssignedJob
        fields = ['id', 'assigned_to', 'assigned_by', 'accepted_on', 'completed', 'is_active', 'total_payment', 'job']