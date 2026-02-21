from rest_framework import serializers
from app.accounts.models import CustomerUser
from app.dashboard.models import PrivacyPolicy,TermsConditions
from app.business_owner.models import Job

class UpdateAccountStatusSerializer(serializers.Serializer):
    account_status = serializers.ChoiceField(choices=CustomerUser.STATUS)

    def update(self, instance, validated_data):
        instance.account_status = validated_data['account_status']
        instance.save()
        return instance


        
        
#
class JobListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.full_name")
    posted_hours_ago = serializers.SerializerMethodField()
    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "created_by",
            "location",
            "pay_type",
            "pay_rate",
            "posted_hours_ago",
            "active_status",
        ]
    def get_posted_hours_ago(self, obj):
        from django.utils.timezone import now
        diff = now() - obj.created_on
        return round(diff.total_seconds() / 3600, 2)

class JobDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.full_name")
    assigned_to = serializers.CharField(source="assigned_to.full_name", default=None)
    completed_by = serializers.CharField(source="completed_by.full_name", default=None)
    class Meta:
        model = Job
        fields = "__all__"
        
class JobListSerializer2(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.full_name")
    total_working_hour = serializers.CharField()
    
    class Meta:
        model = Job
        fields = ['id','title', 'created_by', 'location', 'start_time', 'end_time', 'date', 'total_working_hour', 
                  'pay_type', 'pay_rate', 'job_types']
        

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['content']

class TermsConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsConditions
        fields = ['content']
