from rest_framework import serializers
from app.accounts.models import ReportUserModel
from app.message.ai_helper.report_checker import report_checking

# def report_checking(reported_reason, additional_details):
#     if "offensive" in reported_reason.lower() or "abusive" in additional_details.lower():
#         return "Offensive Content Detected", "high"
#     elif "spam" in reported_reason.lower():
#         return "Spam Behavior", "medium"
#     else:
#         return "Normal Behavior", "low"
    
    
class ReportUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ReportUserModel
        fields = [
            'reported_id', 'reported_to', 'reported_reason', 'additional_details',
            'case_status', 'ai_flag_title', 'ai_flagged_responsed', 'ai_flag',
            'reported_by', 'reported_on', 'updated_on'
        ]
        read_only_fields = ['reported_by', 'reported_on', 'updated_on']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['reported_by'] = user

        report = ReportUserModel.objects.create(**validated_data)

        ai_title, ai_flag = report_checking(report.reported_reason, report.additional_details)

        report.ai_flag_title = ai_title
        report.ai_flag = ai_flag
        report.ai_flagged_responsed = True
        report.save()

        return report

 
class ReportDetailSerializer(serializers.ModelSerializer):
    reported_by = serializers.CharField(source="reported_by.full_name")
    reported_to = serializers.CharField(source="reported_to.full_name")
    class Meta:
        model = ReportUserModel
        fields = [
            'reported_id', 'reported_to', 'reported_reason', 'additional_details',
            'case_status', 'ai_flag_title', 'ai_flagged_responsed', 'ai_flag',
            'reported_by', 'reported_on'
        ]
        
    def to_representation(self, instance):
        """Override the to_representation method to organize fields in sections"""
        data = super().to_representation(instance)
        
        if 'additional_details' in data:
            data['additional_details'] = data['additional_details'][:30]
        return {
            'complaint_information': {
                'report_id':data["reported_id"],
                'reported_on':data["reported_on"],
                'type': data['ai_flag_title'],
                'filled_by': data['reported_by'],
                'reported_user': data['reported_to'],
                'platform': "Direct Report",
                'summary': data['reported_reason'],
                'case_status':data['case_status'],
                'additional_details':data["additional_details"],
                'case_priority':data['ai_flag']

            }
        }

class ReportMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1024, required=True)