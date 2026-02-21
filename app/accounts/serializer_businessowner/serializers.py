from app.accounts.serializer_base.serializers import CustomerUserSerializer,serializers
from app.accounts.models_profile import BusinessOwnerProfile
from django.core.exceptions import ValidationError
from datetime import datetime

class BusinessOwnerProfileSerializer(serializers.ModelSerializer):
    user = CustomerUserSerializer()

    class Meta:
        model = BusinessOwnerProfile
        fields = [
            'user', 
            'image', 
            'business_name', 
            'business_type', 
            'business_address', 
            'contact_person_name', 
            'business_phone', 
            'business_license_number', 
            'business_description', 
            'business_license_document', 
            'hourly_pay_rate', 
            'preferred_job_types', 
            'work_time', 
            'weekly_schedule', 
            'digital_sign', 
            'agree'
        ]
    
    def validate_license_expiry_date(self, value):
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

        profile = BusinessOwnerProfile.objects.create(user=user, **validated_data)
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

        # Update the rest of the fields in BusinessOwnerProfile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the profile instance after updating fields
        instance.save()
        
        return instance