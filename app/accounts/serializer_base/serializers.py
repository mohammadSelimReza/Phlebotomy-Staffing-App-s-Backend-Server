from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from app.accounts.models import NotificationModel,ActivityLog


CustomUser = get_user_model()

class CustomerUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['user_id','full_name', 'email', 'phone', 'gender', 'birth_date', 'role', 'password','account_status']
    
    def validate_role(self, value):
        # Make sure the role is one of the valid choices from ROLE_CHOICES
        valid_roles = [CustomUser.ADMIN, CustomUser.USER, CustomUser.PHLEBOTOMIST, CustomUser.BUSINESS_OWNER]
        if value not in valid_roles:
            raise ValidationError(f"Invalid role: {value}")
        return value
    
    
    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user
class SearchUserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    business_name = serializers.SerializerMethodField()
    years_of_experience = serializers.SerializerMethodField()
    speciality = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['user_id', 'full_name', 'business_name', 'image', 'years_of_experience', 'speciality', 'role']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data['role'] == 'phlebotomist':
            data['years_of_experience'] = self.get_years_of_experience(instance)
            data['speciality'] = self.get_speciality(instance)
            data['image'] = self.get_image(instance)
        elif data['role'] == 'business_owner':
            data['business_name'] = self.get_business_name(instance)
            data['image'] = self.get_image(instance)

        if 'role' in data:
            if data['role'] == 'phlebotomist':
                return{
                    'id':data['user_id'],
                    'name':data['full_name'],
                    'image':data['image'],
                    'years_of_experience':data['years_of_experience'],
                    'speciality':data['speciality'],
                    'role':data['role']
                }
            elif data['role'] == 'business_owner':
                return{
                    'id':data['user_id'],
                    'name':data['full_name'],
                    'image':data['image'],
                    'business_name':data['business_name'],
                    'role':data['role']
                }

    def get_image(self, obj):
        """Get the profile image for phlebotomists and business owners, return empty string if profile doesn't exist"""
        if obj.role == CustomUser.PHLEBOTOMIST:
            profile = obj.phlebotomist_profile if hasattr(obj, 'phlebotomist_profile') else None
        elif obj.role == CustomUser.BUSINESS_OWNER:
            profile = obj.business_owner_profile if hasattr(obj, 'business_owner_profile') else None
        else:
            return ""  # Return empty string if no profile exists

        return profile.image if profile and profile.image else ""

    def get_business_name(self, obj):
        """Return business name only for business owners, empty string if no profile exists"""
        if obj.role == CustomUser.BUSINESS_OWNER:
            return obj.business_owner_profile.business_name if hasattr(obj, 'business_owner_profile') else ""
        return ""

    def get_years_of_experience(self, obj):
        """Return years of experience only for phlebotomists, empty string if no profile exists"""
        if obj.role == CustomUser.PHLEBOTOMIST:
            return obj.phlebotomist_profile.years_of_experience if hasattr(obj, 'phlebotomist_profile') else ""
        return ""

    def get_speciality(self, obj):
        """Return speciality only for phlebotomists, empty string if no profile exists"""
        if obj.role == CustomUser.PHLEBOTOMIST:
            return obj.phlebotomist_profile.speciality if hasattr(obj, 'phlebotomist_profile') else ""
        return ""



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationModel
        fields = ['id', 'title', 'info', 'is_read', 'created_on']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'title', 'info', 'log_time']