from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .models import Message,InappropriateMessageReport
from .serializers import MessageSerializer,InappropriateMessageReportDetailSerializer,InappropriateMessageReportListSerializer,CustomerUserSerializer
from django.contrib.auth import get_user_model
from app.accounts.models import NotificationModel
from django.db.models import Q

User = get_user_model()

def message_checker(text_message):
    # Write your ai logic
    #
    #
    # return Response:
    if "bad"  in text_message.lower():
        return {
            "ai_approval_status": "inappropriate",
            "reported_reason": "Profanity detected",
            "reported_title": "Inappropriate Language"
        }
    else:
        return {
            "ai_approval_status": "approved",
        }

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user
        receiver_id = request.data.get("receiver_id")
        message_type = request.data.get('message_type', 'text')
        content = request.data.get('content', '')
        file_url = request.data.get('file_url', None)

        if sender.role == "phlebotomist":
            try:
                receiver = User.objects.get(id=receiver_id, role="business_owner")
            except User.DoesNotExist:
                return Response({"error": "Receiver must be a Business Owner."}, status=status.HTTP_400_BAD_REQUEST)
        elif sender.role == "business_owner":
            try:
                receiver = User.objects.get(id=receiver_id, role="phlebotomist")
            except User.DoesNotExist:
                return Response({"error": "Receiver must be a Phlebotomist."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "You are not authorized to send messages."}, status=status.HTTP_403_FORBIDDEN)

        ai_response = message_checker(content)

        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            content=content,
            file_url=file_url,
            ai_approval_status=ai_response["ai_approval_status"],
            admin_decision="approved"
        )

        if ai_response["ai_approval_status"] == "inappropriate":
            InappropriateMessageReport.objects.create(
                sender=sender,
                receiver=receiver,
                assigned_job="AI moderation",
                reported_reason=ai_response["reported_reason"],
                reported_title=ai_response["reported_title"],
                message_content=content,
                admin_decision="pending"
            )

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sender = request.user
        receiver_id = request.query_params.get('receiver_id')  # Receiver ID passed in query parameters

        try:
            # Make sure to use the correct model (CustomerUser) instead of User
            receiver = User.objects.get(user_id=receiver_id)  # Assuming user_id is the field in your CustomerUser model

            # Retrieve messages between sender and receiver, filtering by approval status
            messages = Message.objects.filter(
                (Q(sender=sender) & Q(receiver=receiver)) |
                (Q(sender=receiver) & Q(receiver=sender))
            ).filter(
                Q(ai_approval_status="approved") | Q(sender=sender, ai_approval_status="inappropriate")
            ).order_by('sent_on')  # Order messages by timestamp

            return Response(MessageSerializer(messages, many=True).data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND)



class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sender = request.user
        
        # Retrieve all users the current user has chatted with
        chat_partners = Message.objects.filter(
            Q(sender=sender) | Q(receiver=sender)
        ).values('sender', 'receiver').distinct().order_by('-sent_on') 

        # Extract unique user ids
        user_ids = set()
        for chat in chat_partners:
            user_ids.add(chat['sender'])
            user_ids.add(chat['receiver'])

        # Exclude the current user
        user_ids.discard(sender.user_id)

        # Retrieve the users by their ids (use CustomerUser instead of User)
        users = User.objects.filter(user_id__in=user_ids)

        # Serialize the users and return the response (use UserSerializer)
        serializer = CustomerUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InappropriateMessageReportListView(APIView):
    def get(self, request):
        reports = InappropriateMessageReport.objects.all().order_by("-created_on")
        serializer = InappropriateMessageReportListSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class InappropriateMessageReportDetailView(APIView):
    def get(self, request, report_id):
        try:
            report = InappropriateMessageReport.objects.get(id=report_id)
            serializer = InappropriateMessageReportDetailSerializer(report)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InappropriateMessageReport.DoesNotExist:
            return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)
class AdminActionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        report_id = request.query_params.get('report_id')
        action = request.query_params.get('action')
        try:
            # Retrieve the InappropriateMessageReport by report_id
            report = InappropriateMessageReport.objects.get(id=report_id)

            # Retrieve the specific message that was flagged
            message = report.message

            # Check if message exists before performing any actions
            if message is None:
                return Response({"error": "Message not found for this report."}, status=status.HTTP_404_NOT_FOUND)

            if action == 'delete':
                # Mark the message and the report as deleted
                message.admin_decision = 'delete'
                report.admin_decision = 'delete'

                # Save the changes to the message and report
                message.save()
                report.save()

                return Response({"message": "Message deleted successfully."}, status=status.HTTP_200_OK)

            elif action == 'approve':
                # Approve the message and content (set ai_approval_status and admin_decision to 'approved')
                message.ai_approval_status = 'approved'
                message.admin_decision = 'approved'
                report.admin_decision = 'approved'

                message.save()
                report.save()

                return Response({"message": "Message approved successfully."}, status=status.HTTP_200_OK)

            elif action == 'suspend':
                sender = report.sender
                sender.is_active = False
                sender.save()

                NotificationModel.objects.create(
                    user=request.user,
                    title="Inappropiate message detected",
                    info=f"sent inappropiate message to {sender.full_name}"
                )
                
                return Response({"message": f"User {sender.full_name} has been suspended."}, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        except InappropriateMessageReport.DoesNotExist:
            return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)
        except Message.DoesNotExist:
            return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)
