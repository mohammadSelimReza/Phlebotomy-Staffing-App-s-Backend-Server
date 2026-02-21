from app.accounts.serializer_base.serializers import CustomerUserSerializer,serializers
from app.accounts.models_profile import PhlebotomistProfile
from django.core.exceptions import ValidationError
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()



class PhlebotomistProfileSerializer(serializers.ModelSerializer):
    user = CustomerUserSerializer()
    
    class Meta:
        model = PhlebotomistProfile
        fields = [
            'user', 
            'image', 
            'license_number', 
            'license_expiry_date', 
            'years_of_experience', 
            'speciality', 
            'license_document_upload', 
            'identification_upload', 
            'work_preferable', 
            'service_area', 
            'weekly_schedule', 
            'skills'
        ]
        
    
    
    def validate_license_expiry_date(self, value):
        """Ensure the license expiry date is not in the past."""
        if value < datetime.now().date():
            raise ValidationError("License expiry date must be in the future.")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = CustomerUserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
        else:
            raise ValidationError(user_serializer.errors)
        
        profile = PhlebotomistProfile.objects.create(user=user, **validated_data)
        
        return profile
    
    def update(self, instance, validated_data):
            # Update the nested user object (CustomerUser) if present in the data
            user_data = validated_data.pop('user', {})
            
            if user_data:
                user_serializer = CustomerUserSerializer(instance.user, data=user_data, partial=True)  # Allow partial update for the user
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    raise ValidationError(user_serializer.errors)

            # Update the rest of the fields in PhlebotomistProfile
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            # Save the profile instance after updating fields
            instance.save()
            
            return instance
        
        
        
class PhlebotomistUpdateProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = PhlebotomistProfile
        fields = [
            'user',
            'image', 
            'license_number', 
            'license_expiry_date', 
            'years_of_experience', 
            'speciality', 
            'license_document_upload', 
            'identification_upload', 
            'work_preferable', 
            'service_area', 
            'weekly_schedule', 
            'skills'
        ]

    def validate_license_expiry_date(self, value):
        """Ensure the license expiry date is not in the past."""
        if value < datetime.now().date():
            raise ValidationError("License expiry date must be in the future.")
        return value

    def update(self, instance, validated_data):
        # Update the nested user object (CustomerUser) if present in the data
        user_data = validated_data.pop('user', {})
        
        if user_data:
            user_serializer = CustomerUserSerializer(instance.user, data=user_data, partial=True)  # Allow partial update for the user
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                raise ValidationError(user_serializer.errors)

        # Update the rest of the fields in PhlebotomistProfile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the profile instance after updating fields
        instance.save()
        
        return instance
    
    
class PhlebotomistHomePageSerializer(serializers.Serializer):
    total_earning = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_jobs_done = serializers.IntegerField()
    total_rating = serializers.FloatField()
    total_pending_payout = serializers.DecimalField(max_digits=10, decimal_places=2)

    next_job_details = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()

    def get_next_job_details(self, obj):
        return {
            "date": "2025-12-10",
            "start_time": "09:00 AM",
            "end_time": "11:00 AM",
            "job_creator_name": "John Doe",
            "job_title": "Blood Collection",
            "address":"mew mew",
        }

    def get_recent_activity(self, obj):
        return [
            {
                "activity_title": "Job Completed",
                "job_creator_full_name": "John Doe"
            },
            {
                "activity_title": "Job Assigned",
                "job_creator_full_name": "Jane Smith"
            }
        ]
        



class PhlebotomistProfileSerializerView(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    image = serializers.CharField(read_only=True)
    status = serializers.CharField(default='Certified Phlebotomist', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    job_completed = serializers.IntegerField(default=25, read_only=True)
    experience = serializers.IntegerField(source='years_of_experience', read_only=True)
    license = serializers.CharField(source='license_number', read_only=True)
    certification = serializers.CharField(source='speciality', read_only=True)
    skills = serializers.CharField(read_only=True)
    ratings = serializers.FloatField(default=4.6, read_only=True)
    total_rated_clients = serializers.IntegerField(default=120, read_only=True)

    class Meta:
        model = PhlebotomistProfile
        fields = [
            'full_name', 'image', 'status', 'gender', 'job_completed', 
            'experience', 'license', 'certification', 'skills', 
            'ratings', 'total_rated_clients'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Customize the representation
        profile_data = {
            'Phlebotomist Profile': {
                'Full Name': data['full_name'],
                'Image': data['image'],
                'Status': data['status'],
                'Gender': data['gender'],
                'Job Completed': data['job_completed'],
                'Experience': f"{data['experience']} years",
                'License': data['license'],
                'Certification': data['certification'],
                'Skills': data['skills'],
                'Ratings': data['ratings'],
                'Total Rated Clients': data['total_rated_clients'],
            }
        }

        return profile_data
