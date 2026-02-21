from rest_framework import serializers
from .models import Message,InappropriateMessageReport
from django.utils.timezone import localtime
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name")
    receiver_name = serializers.CharField(source="receiver.full_name")
    ai_approval_status = serializers.CharField()

    class Meta:
        model = Message
        fields = ['sender_name', 'receiver_name', 'content', 'file_url', 'message_type', 'ai_approval_status', 'sent_on']



#

class InappropriateMessageReportListSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.CharField(source="sender.full_name")
    receiver_full_name = serializers.CharField(source="receiver.full_name")
    reported_title = serializers.CharField()
    reported_reason = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    report_id = serializers.CharField(source="id")
    
    class Meta:
        model = InappropriateMessageReport
        fields = ['sender_full_name', 'receiver_full_name', 'reported_title', 'reported_reason', 'time_ago', 'report_id']

    def get_reported_reason(self, obj):
        return obj.reported_reason[:30]

    def get_time_ago(self, obj):
        time_diff = localtime(obj.created_on) - localtime()
        return str(abs(time_diff.days)) + " days ago" if time_diff.days != 0 else str(abs(time_diff.seconds // 3600)) + " hours ago"
    
    def to_representation(self, instance):
        """Override the to_representation method to organize fields in sections"""
        data = super().to_representation(instance)

        return {
           'id':data['report_id'],
           'reason':data['reported_title'],
           'title': f"Message from {data['sender_full_name']} to {data['receiver_full_name']}",
           'info': data['reported_reason'],
           'time': data['time_ago']
        }
    
class InappropriateMessageReportDetailSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.CharField(source="sender.full_name")
    sender_image = serializers.ImageField(source="sender.phlebotomist_profile.image", required=False)
    sender_user_id = serializers.CharField(source="sender.user_id")
    receiver_full_name = serializers.CharField(source="receiver.full_name")
    receiver_image = serializers.ImageField(source="receiver.phlebotomist_profile.image", required=False)
    receiver_user_id = serializers.CharField(source="receiver.user_id")
    assigned_job = serializers.CharField()
    reported_title = serializers.CharField()
    reported_reason = serializers.CharField()
    created_on = serializers.DateTimeField()

    class Meta:
        model = InappropriateMessageReport
        fields = [
            'sender_full_name', 'sender_image', 'sender_user_id',
            'receiver_full_name', 'receiver_image', 'receiver_user_id',
            'assigned_job', 'reported_title', 'reported_reason', 'created_on'
        ]


class CustomerUserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    dummy_last_message = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['user_id', 'full_name','image','dummy_last_message'] 
    
    def get_dummy_last_message(self,obj):
        return "This dummy to keep working"
            
    def get_image(self, obj):
        # Check if the user has a Phlebotomist Profile
        if hasattr(obj, 'phlebotomist_profile') and obj.phlebotomist_profile.image:
            return obj.phlebotomist_profile.image
        # Check if the user has a BusinessOwner Profile
        elif hasattr(obj, 'business_owner_profile') and obj.business_owner_profile.image:
            return obj.business_owner_profile.image
        return None