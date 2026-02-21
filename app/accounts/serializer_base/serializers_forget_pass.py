from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from app.accounts.models import PasswordResetOTP
from django.core.mail import send_mail
from django.utils import timezone
import random

User = get_user_model()

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("No user found with this email address.")
        return value
    
    def save(self):
        email = self.validated_data['email']
        otp = str(random.randint(4321, 9876))
        PasswordResetOTP.objects.update_or_create(email=email, defaults={'otp': otp})
        
        # Send OTP to email
        send_mail(
            "Your OTP for password reset", 
            f"Your OTP for password reset is {otp}",
            "selim.reza.uits@gmail.com",
            [email]
        )

        return email

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        otp_record = PasswordResetOTP.objects.filter(email=data['email']).first()
        if not otp_record:
            raise ValidationError("Invalid OTP request.")
        if otp_record.is_expired():
            raise ValidationError("OTP has expired.")
        if otp_record.otp != data['otp']:
            raise ValidationError("Invalid OTP.")
        return data

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("No user found with this email address.")
        return value

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return user
