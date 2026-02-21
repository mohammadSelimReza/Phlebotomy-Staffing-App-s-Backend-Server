from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self,full_name,email,phone,gender,birth_date,role,password=None):
        valid_roles = [self.model.ADMIN, self.model.USER, self.model.PHLEBOTOMIST, self.model.BUSINESS_OWNER]
        if role not in valid_roles:
            raise ValidationError(f"Invalid role: {role}")

        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(
            full_name=full_name,
            email=email,
            phone=phone,
            gender=gender,
            birth_date=birth_date,
            role=role
        )
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,full_name,email,phone,gender,birth_date,role,password):
        valid_roles = [self.model.ADMIN, self.model.USER, self.model.PHLEBOTOMIST, self.model.BUSINESS_OWNER]
        if role not in valid_roles:
            raise ValidationError(f"Invalid role: {role}")
        user = self.model(
            full_name=full_name,
            email=email,
            phone=phone,
            gender=gender,
            birth_date=birth_date,
            role=role
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.set_password(password) 
        user.save(using=self._db)
        return user