from rest_framework import serializers
from app.accounts.models import CustomerUser,NotificationModel,ActivityLog
from app.accounts.models_profile import BusinessOwnerProfile
from app.business_owner.models import Job,TempAssignedJob,RequestForJob,CompletedAssignedJob
from decimal import Decimal
from django.utils import timezone

class JobSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all(), required=False)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all(), required=False, allow_null=True)
    completed_by = serializers.PrimaryKeyRelatedField(queryset=CustomerUser.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'profession_type', 'job_info', 'location', 'date', 'start_time', 'end_time', 
            'total_working_hour', 'pay_type', 'pay_rate', 'job_types', 'assigned', 'assigned_to', 
            'completed', 'completed_by', 'created_by', 'created_on', 'updated_on'
        ]

    def create(self, validated_data):
        # Assign the 'created_by' field to the current user from the request context
        request = self.context.get('request')
        validated_data['created_by'] = request.user  # Automatically set created_by to the user making the request
        
        job = Job.objects.create(**validated_data)
        
        NotificationModel.objects.create(
            user=request.user,
            title="New Job Posted",
            info=f"post a new job: '{job.title}'."
        )

        ActivityLog.objects.create(
            user=request.user,
            title="New Job Posted",
            info=f"posted a new job: '{job.title}'."
        )
        return job



class JobFilterSerializer(serializers.Serializer):
    filter_option = serializers.ChoiceField(choices=['all', 'new', 'assigned', 'completed'])


class JobPhlebotomistFilterSerializer(serializers.Serializer):
    job_types = serializers.ChoiceField(choices=Job.JOB_TYPE_CHOICES)




class TempAssignedJobSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    assigned_to_full_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    assigned_by_full_name = serializers.CharField(source='assigned_by.full_name', read_only=True)

    class Meta:
        model = TempAssignedJob
        fields = [
            'id', 'job', 'job_title', 'assigned_to', 'assigned_to_full_name', 'assigned_by', 
            'assigned_by_full_name', 'assignment_start_time', 'assignment_end_time', 'status','is_accepted', 'is_active', 
            'created_on', 'updated_on'
        ]
        
class JobListSerializer(serializers.ModelSerializer):
    created_by_full_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'profession_type', 'start_time', 'end_time', 'date', 'pay_rate', 'total_working_hour', 'created_by_full_name'
        ]


class JobDetailsViewSerializser(serializers.ModelSerializer):
    creator_by_id = serializers.CharField(source='created_by.user_id',read_only=True)
    created_by_full_name = serializers.CharField(source='created_by.full_name', read_only=True)
    client_full_name = serializers.CharField(source='created_by.full_name', read_only=True)
    client_address = serializers.CharField(source='created_by.business_owner_profile.business_address', read_only=True)
    client_phone = serializers.CharField(source='created_by.phone', read_only=True)
    
    job_id = serializers.CharField(source='id', read_only=True)
    total_payment = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'job_id', 'client_full_name', 'client_address', 'client_phone',
            'title', 'date', 'start_time', 'end_time', 'total_working_hour',
            'pay_rate', 'total_payment', 'created_by_full_name','creator_by_id'
        ]
    
    def get_total_payment(self, obj):
        """Calculate total payment"""
        # Extract total working hours in 'HH:MM:SS' format
        total_working_hour = obj.total_working_hour
        
        # Split the time string into hours, minutes, and seconds
        try:
            hours, minutes, seconds = map(int, total_working_hour.split(':'))
        except ValueError:
            return Decimal(0)  # Return Decimal(0) if the format is invalid
        
        # Convert the time into hours (float)
        total_hours = hours + minutes / 60 + seconds / 3600
        
        # Convert total_hours to Decimal for compatibility with pay_rate
        total_hours_decimal = Decimal(total_hours)
        
        # Calculate total payment based on pay_rate and total_hours
        total_payment = obj.pay_rate * total_hours_decimal
        return total_payment
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Customizing the representation as per the requested format
        job_info = {
            "Job Information": {
                "job title": data['title'],
                "job date": data['date'],
                "start time to end time": f"{data['start_time']} to {data['end_time']}",
                "total working hours": data['total_working_hour'],
                "job id": data['job_id'],
                "hourly rate": data['pay_rate'],
                "total hour": data['total_working_hour'],
                "total payment": data['total_payment']
            }
        }
        
        client_info = {
            "Client Information": {
                "business_owner_id":data['creator_by_id'],
                "business owner": data['client_full_name'],
                "address": data['client_address'],
                "phone": data['client_phone']
            }
        }
        
        # Combine both sections
        result = {**client_info, **job_info}
        return result


class JobListForPhlebotomistSerializer(serializers.ModelSerializer):
    business_owner_name = serializers.CharField(source='created_by.full_name', read_only=True)
    applied = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'profession_type', 'start_time', 'end_time', 'date', 'pay_rate', 'total_working_hour', 'job_types',
            'business_owner_name','location', 'applied'
        ]
    
    def get_applied(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return RequestForJob.objects.filter(job=obj, requested_by=user).exists()
        return False
        
class JobAllListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="title")
    hospital_name = serializers.SerializerMethodField()
    
    def get_hospital_name(self,obj):
        return obj.created_by.full_name
    
    class Meta:
        model = Job
        fields = [
            'id','title','full_name',"hospital_name"
        ]
        
        
class RequestForJobSerializer(serializers.ModelSerializer):
    requested_by_full_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    requested_by_email = serializers.EmailField(source='requested_by.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = RequestForJob
        fields = [
            'id',
            'job_title',
            'requested_by_full_name',
            'requested_by_email',
            'status',
            'is_active',
            'requested_on',
            'updated_on',
        ]
        
        
class BusinessOwnerDashboardSerializer(serializers.Serializer):
    total_pending_assignments = serializers.IntegerField()
    total_new_applicants = serializers.IntegerField()
    notifications = serializers.SerializerMethodField()

    def get_notifications(self, obj):
        notifications = NotificationModel.objects.filter(user=obj).order_by('-created_on')[:3]
        return [
            {
                "title": notification.title,
                "info": notification.info,
                "time_ago": self.time_diff(notification.created_on)
            }
            for notification in notifications
        ]

    def time_diff(self, timestamp):
        delta = timezone.now() - timestamp
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600} hours ago"
        else:
            return f"{delta.seconds // 60} minutes ago"

    def to_representation(self, instance):
        total_pending_assignments = Job.objects.filter(created_by=instance, assigned=False).count()

        total_new_applicants = RequestForJob.objects.filter(job__created_by=instance, status='pending').count()

        return {
            'total_pending_assignments': total_pending_assignments,
            'total_new_applicants': total_new_applicants,
            'notifications': self.get_notifications(instance)
        }
        
class BusinessOwnerProfileSerializer(serializers.ModelSerializer):
    # Serializer for BusinessOwnerProfile
    user_id = serializers.CharField(source='user.user_id')
    full_name = serializers.CharField(source='user.full_name')
    role = serializers.CharField(source='user.role')
    image = serializers.URLField()
    business_name = serializers.CharField()
    business_type = serializers.CharField()
    business_address = serializers.CharField()
    contact_person_name = serializers.CharField()
    business_phone = serializers.CharField()
    business_license_number = serializers.CharField()
    business_description = serializers.CharField()
    hourly_pay_rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    preferred_job_types = serializers.JSONField()
    work_time = serializers.CharField()
    weekly_schedule = serializers.JSONField()


    class Meta:
        model = BusinessOwnerProfile
        fields = [
            'user_id', 'full_name', 'role', 'image', 'business_name', 'business_type', 'business_address',
            'contact_person_name', 'business_phone', 'business_license_number', 'business_description',
            'hourly_pay_rate', 'preferred_job_types', 'work_time', 'weekly_schedule'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    business_owner_profile = BusinessOwnerProfileSerializer()

    class Meta:
        model = CustomerUser
        fields = ['user_id', 'full_name', 'email', 'phone', 'gender', 'birth_date', 'role', 'account_status', 'business_owner_profile']
        
        
class CompletedAssignedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedAssignedJob
        fields = ['job', 'completed_by', 'assigned_by', 'payment_status', 'completed_on', 'is_active']