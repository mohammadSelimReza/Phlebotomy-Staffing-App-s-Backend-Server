import random
import stripe
from django.db import transaction
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from app.accounts.models import AppointmentModel,ReportUserModel
from app.accounts.serializer_base.serializers import SearchUserSerializer,NotificationSerializer,ActivityLogSerializer
from app.accounts.serializer_base.serializers_report import ReportUserSerializer,ReportDetailSerializer,ReportMessageSerializer
from app.accounts.serializer_base.serializers_appointment import AppointmentSerializer,AppointmentListSerializer,AppointmentDetailSerializer,AppointmentInfoSerializer,AppointmentDetailSerializerView,AppointmentViewInfoSerializer
from app.accounts.serializer_base.serializers_forget_pass import ResetPasswordSerializer
from app.accounts.serializer_phlebotomist.serializers import PhlebotomistProfileSerializer,PhlebotomistHomePageSerializer,PhlebotomistProfileSerializerView
from app.accounts.serializer_businessowner.serializers import BusinessOwnerProfileSerializer
from app.accounts.serializer_base.serializers_job import PhlebotomistJobHistorySerializer
from app.business_owner.models import CompletedAssignedJob
from app.accounts.models_profile import PhlebotomistProfile
from app.accounts.email_sent import send_mail
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from app.accounts.models import PasswordResetOTP,NotificationModel,ActivityLog
from app.business_owner.models import Job,AcceptedAssignedJob
from app.accounts.email_sent import send_warning_email,send_suspened_email
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from app.business_owner.serializers import JobAllListSerializer
from rest_framework.parsers import MultiPartParser,JSONParser
from django.db.models import Q


from django.db.models import Sum

User = get_user_model()



class PhlebotomistSignUpView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    def post(self, request, *args, **kwargs):
        serializer = PhlebotomistProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Phlebotomist successfully signed up!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class BusinessOwnerSignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BusinessOwnerProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Business Owner successfully signed up!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.account_status == User.APPROVED:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                response_data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "username": user.username,
                    "full_name": user.full_name,
                    "gender": user.gender,
                    "email": user.email,
                    "role": user.role
                }
                
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                if user.account_status == User.PENDING:
                    return Response({"message": "Your account is currently under review."}, status=status.HTTP_403_FORBIDDEN)
                elif user.account_status == User.REJECTED:
                    return Response({"message": "Your account has been rejected."}, status=status.HTTP_403_FORBIDDEN)
                
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#


class SendOTPView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate if the user exists
        if not User.objects.filter(email=email).exists():
            return Response({"error": "No user found with this email address."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate OTP
        otp = str(random.randint(4321, 9876))
        
        # Store OTP in the database
        PasswordResetOTP.objects.update_or_create(email=email, defaults={'otp': otp})
        
        # Send OTP to the email
        try:
            send_mail(
                "Your OTP for password reset",
                f"Your OTP for password reset is {otp}",
                "srreza1999@gmail.com",
                [email]
            )
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "OTP sent successfully to the provided email."
        }, status=status.HTTP_200_OK)
        
        
class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the OTP record based on the provided email
        otp_record = PasswordResetOTP.objects.filter(email=email).first()

        if not otp_record:
            return Response({"error": "No OTP request found for this email."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP has expired (5 minutes validity)
        if self.is_otp_expired(otp_record.created_at):
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify if the OTP matches
        if otp_record.otp != otp:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "OTP verified successfully. You can now reset your password."
        }, status=status.HTTP_200_OK)

    def is_otp_expired(self, created_at):
        """
        Check if the OTP is expired. OTP expires 5 minutes after creation.
        """
        # Make both datetimes aware (or both naive, but here we convert them to aware)
        created_at = timezone.localtime(created_at)  # Convert to local time with timezone info
        return created_at + timedelta(minutes=5) > timezone.localtime(timezone.now())  # Convert now to local time
    
class ResetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Password reset successful."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class JobAllListView(APIView):
    def get(self,request,*args, **kwargs):
        model = Job.objects.filter(active_status="approved")
        serializer = JobAllListSerializer(model,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class CreateAppointmentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AppointmentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            appointment = serializer.save()  # DRF will call the 'create' method automatically

            return Response({
                "message": "Appointment created successfully",
                "appointment_id": appointment.appointment_id,
                "test_package": appointment.test_package.title,  # Assuming `title` field exists in `Job`
                "created_date": appointment.created_on.date(),
                "created_time": appointment.created_on.time(),
                "initial_fee": appointment.initial_fee,
                "service_fee": appointment.service_fee,
                "tax_fee": appointment.tax_fee,
                "total_fee": appointment.total,  # Should now reflect the correct total
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

stripe.api_key = settings.STRIPE_SECRET_KEY

class UpdateBillingAndCreateStripeCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        appointment_id = request.data.get('appointment_id')
        street_address = request.data.get('street_address')
        city = request.data.get('city')
        state = request.data.get('state')
        zip_code = request.data.get('zip_code')

        with transaction.atomic():
            try:
                appointment = AppointmentModel.objects.get(appointment_id=appointment_id)
            except AppointmentModel.DoesNotExist:
                return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

            appointment.street_address = street_address
            appointment.city = city
            appointment.state = state
            appointment.zip_code = zip_code
            appointment.save()

            amount = int(appointment.total * 100)

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f"Appointment for {appointment.user.full_name}",
                            },
                            'unit_amount': amount,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url = f"{settings.FRONTEND_URL}/payment-success/?booking_id={appointment_id}",
                cancel_url=f'{settings.FRONTEND_URL}/payment-cancel/',
                customer = None,
                customer_email=appointment.user.email,
                metadata={
                    'payment_type': 'serviceRequest',
                    'appointment_id': appointment_id
                },
            )
            
            return Response({
                "message": "Billing address updated and Stripe checkout session created successfully",
                "session_id": session.id,
                "payment_url":session.url,
                "appointment_id": appointment.appointment_id
            }, status=status.HTTP_200_OK)

            
            
            
STRIPE_WEBHOOK_SECRET = "whsec_83e7ed6e6a31e5abe139a0cbbbc28185e68568e63f800246636366b9fad71563"

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            print(str(e))
            return JsonResponse({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            print(str(e))
            return JsonResponse({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)


        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            if session.get('metadata', {}).get('payment_type') == 'serviceRequest':
                appointment_id = session.get('metadata', {}).get('appointment_id')
                try:
                    appointment = AppointmentModel.objects.get(appointment_id=appointment_id)
                    appointment.payment_status = True
                    appointment.save()
                    return JsonResponse({"message": "Payment successful, appointment updated."}, status=status.HTTP_200_OK)
                except AppointmentModel.DoesNotExist:
                    return JsonResponse({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return JsonResponse({'message': 'Event received and processed'}, status=status.HTTP_200_OK)
    
    
# Admin Patient View:

class AppointmentListView(generics.ListAPIView):
    queryset = AppointmentModel.objects.filter(payment_status=True)
    serializer_class = AppointmentListSerializer
    permission_classes = [IsAdminUser]
    
class AppointmentDetailView(generics.RetrieveAPIView):
    queryset = AppointmentModel.objects.all()
    serializer_class = AppointmentDetailSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'appointment_id'
    
    
class ReportCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReportUserSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            report = serializer.save()
            return Response({"success":"You report has be submitted.","report_id":report.reported_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class ReportListView(generics.ListAPIView):
    queryset = ReportUserModel.objects.all()
    serializer_class = ReportDetailSerializer
    permission_classes = [IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        total_pending_count = ReportUserModel.objects.filter(case_status=ReportUserModel.PENDING).count()

        total_solved_count = ReportUserModel.objects.filter(case_status=ReportUserModel.SOLVED).count()

        today_start = timezone.now().date()
        today_end = today_start + timedelta(days=1)

        total_solved_today_count = ReportUserModel.objects.filter(
            case_status=ReportUserModel.SOLVED,
            reported_on__gte=today_start,
            reported_on__lt=today_end
        ).count()

        reports = self.get_queryset()

        serialized_reports = ReportDetailSerializer(reports, many=True).data

        response_data = {
            'summary': {
                'total_pending_count': total_pending_count,
                'total_solved_count': total_solved_count,
                'total_solved_today_count': total_solved_today_count,
            },
            'reports': serialized_reports,
        }

        return Response(response_data)

class ReportDetailView(generics.RetrieveAPIView):
    queryset = ReportUserModel.objects.all()
    serializer_class = ReportDetailSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'reported_id'
    
    
class ReportActionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, reported_id, action):
        try:
            report = ReportUserModel.objects.get(reported_id=reported_id)
            reported_user = report.reported_to
            reporting_user = report.reported_by

            if action == 'warn':
                send_warning_email(reported_user.email, report.reported_reason)
                report.case_status = ReportUserModel.SOLVED
                report.save()
                return Response({"message": "Warning email sent successfully."}, status=status.HTTP_200_OK)

            elif action == 'suspend':
                send_suspened_email(reported_user.email, report.reported_reason)
                reported_user.is_active = False
                reported_user.save()
                report.case_status = ReportUserModel.SOLVED
                report.save()
                return Response({"message": "User suspended successfully."}, status=status.HTTP_200_OK)
            elif action == 'dismiss':
                # Dismiss the case and update the status
                report.case_status = 'dismissed'
                report.save()
                return Response({"message": "Case dismissed successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        except ReportUserModel.DoesNotExist:
            return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
class SendReportMessageView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, reported_id):
        serializer = ReportMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data['message']

            try:
                report = ReportUserModel.objects.get(reported_id=reported_id)
                reported_user = report.reported_to
                reporting_user = report.reported_by

                self.send_message(reported_user.email, message, report.reported_reason)
                self.send_message(reporting_user.email, message, report.reported_reason)

                return Response({"message": "Message sent to both parties successfully."}, status=status.HTTP_200_OK)

            except ReportUserModel.DoesNotExist:
                return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_message(self, recipient_email, message, report_reason):
        subject = "Important: Report Update"
        full_message = f"Dear User,\n\nYou have been notified regarding the following report: {report_reason}\n\nMessage: {message}\n\nBest regards,\nAdmin Team"
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject, full_message, from_email, [recipient_email])
        
        

class SearchPhlebotomist(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')

        if not query:
            return Response({"error": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            matching_users = User.objects.filter(
                Q(full_name__icontains=query) |
                Q(email__icontains=query),
                role=User.PHLEBOTOMIST
            )

            if not matching_users.exists():
                return Response({"message": "No phlebotomists found matching the query."}, status=status.HTTP_404_NOT_FOUND)

            serializer = SearchUserSerializer(matching_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchClientsUser(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')

        if not query:
            return Response({"error": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            matching_users = User.objects.filter(
                Q(full_name__icontains=query) |
                Q(email__icontains=query),
                role=User.BUSINESS_OWNER
            )

            if not matching_users.exists():
                return Response({"message": "No business owners found matching the query."}, status=status.HTTP_404_NOT_FOUND)

            serializer = SearchUserSerializer(matching_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PhlebotomistHomePageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user

        completed_jobs = CompletedAssignedJob.objects.filter(completed_by=user)
        total_earning = sum(job.job.pay_rate for job in completed_jobs)

        total_jobs_done = completed_jobs.count()

        total_pending_payout = sum(job.job.pay_rate for job in completed_jobs if not job.payment_status)

        total_rating = 4.5

        data = {
            'total_earning': total_earning,
            'total_jobs_done': total_jobs_done,
            'total_rating': total_rating,
            'total_pending_payout': total_pending_payout,
        }

        # You can serialize dynamic data such as next_job_details and recent_activity
        serializer = PhlebotomistHomePageSerializer(data)
        return Response(serializer.data)
    
    
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        notifications = NotificationModel.objects.filter(user=request.user).order_by('-created_on')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MarkNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        notification_id = request.query_params.get('notification_id')

        try:
            notification = NotificationModel.objects.get(id=notification_id, user=request.user)
        except NotificationModel.DoesNotExist:
            return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        # Mark the notification as read
        notification.is_read = True
        notification.save()

        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)
    
class ActivityLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        activity_logs = ActivityLog.objects.filter(user=request.user).order_by('-log_time')
        serializer = ActivityLogSerializer(activity_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class PhlebotomistJobHistorySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_month = timezone.now().month
        current_year = timezone.now().year

        job_history = AcceptedAssignedJob.objects.filter(
            assigned_to=request.user
        )

        serializer = PhlebotomistJobHistorySerializer(job_history, many=True)

        total_earnings = AcceptedAssignedJob.objects.filter(
            assigned_to=request.user,
            completed=True,  # Ensure the job is completed
            accepted_on__year=current_year,
            accepted_on__month=current_month
        ).aggregate(Sum('total_payment'))['total_payment__sum'] or 0.00

        total_completed_jobs = AcceptedAssignedJob.objects.filter(
            assigned_to=request.user,
            completed=True,  # Ensure the job is completed
            accepted_on__year=current_year,
            accepted_on__month=current_month
        ).count()

        return Response({
            "total_earnings": total_earnings,
            "total_completed_jobs": total_completed_jobs,
            "job_history": serializer.data
        }, status=status.HTTP_200_OK)
        
class PhlebotomistProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            phlebotomist_profile = PhlebotomistProfile.objects.get(user=request.user)
        except PhlebotomistProfile.DoesNotExist:
            return Response({"error": "Phlebotomist profile not found."}, status=404)

        # Serialize the data
        serializer = PhlebotomistProfileSerializerView(phlebotomist_profile)
        return Response(serializer.data, status=200)
    
    

class BusinessOwnerAppointmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure the current user is a Business Owner
        if request.user.role != User.BUSINESS_OWNER:
            return Response({"error": "You are not authorized to view this appointment list."}, status=403)

        # Fetch all appointments created by the current business owner
        appointments = AppointmentModel.objects.filter(user=request.user)

        # Serialize the data using the new serializer
        serializer = AppointmentInfoSerializer(appointments, many=True)
        return Response(serializer.data, status=200)
    
class AppointmentDetailViewBusiness(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        # Check if the current user is a Business Owner or has access to the appointment
        if request.user.role != User.BUSINESS_OWNER:
            return Response({"error": "You are not authorized to view this appointment."}, status=403)
        
        try:
            appointment = AppointmentModel.objects.get(appointment_id=appointment_id, user=request.user)
        except AppointmentModel.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=404)
        
        # Serialize the appointment details
        serializer = AppointmentDetailSerializerView(appointment)
        return Response(serializer.data, status=200)
    
    
    
    
class BusinessOwnerAppointmentViewListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'business_owner':
            return Response({"error": "You are not authorized to view this appointment list."}, status=status.HTTP_403_FORBIDDEN)
        appointments = AppointmentModel.objects.filter(test_package__created_by=request.user)

        serializer = AppointmentViewInfoSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class BusinessOwnerAppointmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id, *args, **kwargs):
        # Ensure the current user is a business owner
        if request.user.role != 'business_owner':
            return Response({"error": "You are not authorized to view this appointment."}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Fetch the appointment using the appointment_id and verify it belongs to the current business owner
            appointment = AppointmentModel.objects.get(appointment_id=appointment_id, test_package__created_by=request.user)
        except AppointmentModel.DoesNotExist:
            return Response({"error": "Appointment not found or you do not have permission to view this appointment."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data using the existing serializer for appointments
        serializer = AppointmentViewInfoSerializer(appointment)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)