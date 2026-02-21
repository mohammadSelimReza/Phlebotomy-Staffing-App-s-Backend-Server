from datetime import date
from rest_framework import serializers
from app.accounts.models import CustomerUser,AppointmentModel,NotificationModel,ActivityLog

class AppointmentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True)
    gender = serializers.CharField(write_only=True)

    class Meta:
        model = AppointmentModel
        fields = [
            "appointment_id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
            "gender",
            "test_package",
            "start_date",
            "start_date_start_time",
            "start_date_end_time",
            "end_date",
            "end_date_start_time",
            "end_date_end_time",
            "hospital",
            "location",
            "current_medication",
            "prescription",
            "known_allergies",
            "medical_conditions",
            "special_request",
            "email_notification_enable",
            "terms_and_condition_agreement",
            "agreement"
        ]
        read_only_fields = ["appointment_id"]

    def create(self, validated_data):
        # Extract user information
        email = validated_data.pop("email")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        phone = validated_data.pop("phone")
        gender = validated_data.pop("gender")
        dob = validated_data.pop("date_of_birth")
        test_package_id = validated_data.get("test_package")

        # Get or create the user based on the provided email
        user, created = CustomerUser.objects.get_or_create(
            email=email,
            defaults={
                "full_name": f"{first_name} {last_name}",
                "phone": phone,
                "gender": gender,
                "birth_date": dob,
                "role": CustomerUser.USER,
                "is_active": True,
            }
        )

        # Retrieve the job based on the test_package (job id)
        from app.business_owner.models import Job
        job = Job.objects.filter(id=test_package_id, active_status="approved").first()

        if job:
            validated_data["hospital"] = job.created_by.full_name
            validated_data["initial_fee"] = job.pay_rate
            validated_data["service_fee"] = 9  # Example value for service fee
            validated_data["tax_fee"] = 5      # Example value for tax fee
        else:
            validated_data["hospital"] = None
            validated_data["initial_fee"] = 0
            validated_data["service_fee"] = 0
            validated_data["tax_fee"] = 0

        # Create the appointment
        appointment = AppointmentModel.objects.create(user=user, **validated_data)
        
        # Ensure total fee is recalculated after creating the appointment
        appointment.save()  # This will trigger the save method and calculate total_fee

        # Optional: Create notification and activity log for job acceptance
        if job:
            NotificationModel.objects.create(
                user=user,
                title="Job Accepted",
                info=f"accepted the job '{job.title}'."
            )

            ActivityLog.objects.create(
                user=user,
                title="Job Accepted",
                info=f"accepted the job '{job.title}'."
            )

        return appointment


class AppointmentListSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.full_name')
    appointment_id = serializers.CharField()

    class Meta:
        model = AppointmentModel
        fields = ['user_full_name', 'appointment_id']


class AppointmentDetailSerializer(serializers.ModelSerializer):
    # Patient Information
    patient_full_name = serializers.CharField(source='user.full_name')
    patient_age = serializers.SerializerMethodField()
    patient_contact = serializers.CharField(source='user.phone')
    request_date = serializers.DateField(source='start_date')
    request_time = serializers.TimeField(source='start_date_start_time')

    # Client Information
    client_name = serializers.CharField(source='hospital')
    # created_on = serializers.DateTimeField(source='created_on')

    # Service Details
    service_name = serializers.CharField(source='test_package')
    total_amount = serializers.DecimalField(source='total', max_digits=6, decimal_places=2)

    # Medical Information
    prescription = serializers.CharField(allow_blank=True)
    special_instruction = serializers.CharField(source='special_request', allow_blank=True)

    # Location Details
    address = serializers.CharField(source='street_address', allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    state = serializers.CharField(allow_blank=True)
    zip_code = serializers.IntegerField(allow_null=True)

    class Meta:
        model = AppointmentModel
        fields = [
            'patient_full_name', 'patient_age', 'patient_contact', 
            'request_date', 'request_time',
            'client_name', 'created_on',
            'service_name', 'total_amount',
            'prescription', 'special_instruction',
            'address', 'city', 'state', 'zip_code'
        ]

    def get_patient_age(self, obj):
        """Calculate age based on birthdate"""
        birth_date = obj.user.birth_date
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))











class AppointmentInfoSerializer(serializers.ModelSerializer):
    appointment_id = serializers.CharField(read_only=True)
    appointment_title = serializers.CharField(default="New Appointment", read_only=True)
    appointment_info = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentModel
        fields = ['appointment_id', 'appointment_title', 'appointment_info']

    def get_appointment_info(self, obj):
        # Custom message for appointment info
        return f"{obj.user.full_name} has requested this service"



class AppointmentViewInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentModel
        fields = [
            'appointment_id', 'user', 'test_package', 'start_date', 'start_date_start_time', 
            'start_date_end_time', 'end_date', 'end_date_start_time', 'end_date_end_time', 
            'hospital', 'location', 'current_medication', 'prescription', 'known_allergies', 
            'medical_conditions', 'special_request', 'email_notification_enable', 
            'terms_and_condition_agreement', 'agreement', 'initial_fee', 'service_fee', 
            'tax_fee', 'total', 'street_address', 'city', 'state', 'zip_code', 'payment_status', 
            'assigned', 'created_on'
        ]
    
class AppointmentDetailSerializerView(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    
    test_package = serializers.CharField()
    start_date = serializers.DateField()
    start_time = serializers.TimeField(source='start_date_start_time')
    end_time = serializers.TimeField(source='start_date_end_time')
    location = serializers.CharField()
    current_medication = serializers.CharField()
    prescription_url = serializers.CharField(source='prescription', read_only=True)
    known_allergies = serializers.CharField()
    medical_conditions = serializers.JSONField()
    special_request = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    payment_status = serializers.BooleanField()

    class Meta:
        model = AppointmentModel
        fields = [
            'appointment_id', 'user_full_name', 'user_email', 'user_phone', 
            'test_package', 'start_date', 'start_time', 'end_time', 'location',
            'current_medication', 'prescription_url', 'known_allergies', 
            'medical_conditions', 'special_request', 'total_amount', 'payment_status'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # You can customize the representation here if necessary
        data['user_info'] = {
            'full_name': data['user_full_name'],
            'email': data['user_email'],
            'phone': data['user_phone'],
        }
        
        # Remove the redundant individual fields as we're bundling them into `user_info`
        del data['user_full_name']
        del data['user_email']
        del data['user_phone']
        
        return data
    
    
    