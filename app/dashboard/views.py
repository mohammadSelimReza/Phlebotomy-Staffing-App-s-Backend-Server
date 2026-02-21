from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics,permissions
from rest_framework.status import HTTP_200_OK
from app.accounts.models import CustomerUser,NotificationModel,ActivityLog
from app.accounts.models_profile import PhlebotomistProfile
from app.dashboard.serializers import UpdateAccountStatusSerializer
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from app.dashboard.models import TermsConditions,PrivacyPolicy
from app.dashboard.serializers import JobDetailSerializer,JobListSerializer,JobListSerializer2,TermsConditionsSerializer,PrivacyPolicySerializer
from app.accounts.serializer_phlebotomist.serializers import PhlebotomistProfileSerializer

from app.business_owner.models import Job,TempAssignedJob
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class UserManagementListView(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch all users from CustomerUser model
        users = CustomerUser.objects.filter(is_staff=False).order_by('-date_joined')
        users_data = []

        for user in users:
            # Get the associated profile for business owner or phlebotomist
            profile = None
            if hasattr(user, 'business_owner_profile'):
                profile = user.business_owner_profile
            elif hasattr(user, 'phlebotomist_profile'):
                profile = user.phlebotomist_profile

            # Prepare user data with profile information
            user_data = {
                "id":user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "date_joined": user.date_joined,
                "account_status":user.account_status,
                "image": profile.image if profile else None
            }
            users_data.append(user_data)

        return Response({
            "users": users_data
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            # Fetch the user based on user_id
            user = CustomerUser.objects.get(user_id=user_id)

            # Check if user has a profile (either business owner or phlebotomist)
            profile = None
            if hasattr(user, 'business_owner_profile'):
                profile = user.business_owner_profile
            elif hasattr(user, 'phlebotomist_profile'):
                profile = user.phlebotomist_profile

            # Prepare user profile data
            user_data = {
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "phone": user.phone,
                "gender": user.gender,
                "birth_date": user.birth_date,
                "date_joined": user.date_joined,
                "image": profile.image if profile else None,
                "skills": profile.skills if profile else None,
                "service_area": profile.service_area if profile else None,
                "weekly_schedule": profile.weekly_schedule if profile else None,
                "status":user.account_status.capitalize(),
                # You can add more fields as needed
            }

            return Response({
                "user_profile": user_data
            }, status=status.HTTP_200_OK)

        except CustomerUser.DoesNotExist:
            return Response({
                "error": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
            

class UpdateAccountStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user = CustomerUser.objects.get(user_id=user_id)
        except CustomerUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate and update the account status
        serializer = UpdateAccountStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            return Response({
                "message": "Account status updated successfully.",
                "user_id": user.user_id,
                "new_status": user.account_status
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
#


# ======================================================================================

class DashboardDataView(APIView):
    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        pending_users = User.objects.filter(role__in=[User.PHLEBOTOMIST, User.BUSINESS_OWNER], account_status=User.PENDING).count()
        total_approved_jobs = Job.objects.filter(active_status=Job.APPROVED).count()
        revenue_this_month = 5232  # Dummy value for revenue this month
        dashboard_data = {
            "total_users": total_users,
            "pending_verification": pending_users,
            "total_approved_jobs": total_approved_jobs,
            "revenue_this_month": revenue_this_month,
        }

        return Response(dashboard_data, status=status.HTTP_200_OK)
#==========================================================================================

class PendingPhlebotomistListView(APIView):
    def get(self, request, *args, **kwargs):
        pending_phlebotomists = CustomerUser.objects.filter(role='phlebotomist', account_status='pending')
        
        total_pending = pending_phlebotomists.count()
        
        phlebotomist_data = []
        for user in pending_phlebotomists:
            try:
                profile = user.phlebotomist_profile
            except PhlebotomistProfile.DoesNotExist:
                profile = None

            phlebotomist_data.append({
                'id':user.user_id,
                'image': profile.image if profile else None,
                'full_name': user.full_name,
                'status': 'Available',
                'location': profile.service_area if profile else None,
                'years_of_experience': profile.years_of_experience if profile else None
            })
        
        return Response({
            "total_pending": total_pending,
            "phlebotomists": phlebotomist_data
        }, status=status.HTTP_200_OK)


class PendingPhlebotomistDetailView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user = User.objects.get(user_id=user_id, role='phlebotomist', account_status='pending')
            profile = user.phlebotomist_profile
            phlebotomist_details = {
                'image': profile.image if profile else None,
                'full_name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'gender': user.gender,
                'birth_date': user.birth_date,
                'status': user.account_status,
                'years_of_experience': profile.years_of_experience if profile else None,
                'speciality': profile.speciality if profile else None,
                'license_number': profile.license_number if profile else None,
                'service_area': profile.service_area if profile else None,
                'skills': profile.skills if profile else None,
                'license_expiry_date': profile.license_expiry_date if profile else None
            }
            return Response(phlebotomist_details, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Phlebotomist not found"}, status=status.HTTP_404_NOT_FOUND)
        
class AdminApproveRejectPhlebotomistView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        action = request.data.get('action')  # 'approve' or 'reject'
        
        if action not in ['approve', 'reject']:
            return Response({"error": "Invalid action. Choose either 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(user_id=user_id, role='phlebotomist', account_status='pending')
        except User.DoesNotExist:
            return Response({"error": "Phlebotomist not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if action == 'approve':
            user.account_status = 'approved'
        elif action == 'reject':
            user.account_status = 'rejected'
        
        user.save()
        
        NotificationModel.objects.create(
                user=user,
                title="Account Application Approved",
                info="approved by Admin."
            )
        
        return Response({
            "message": f"Phlebotomist account status updated to {user.account_status}."
        }, status=status.HTTP_200_OK)
        
        
#==========================================================================================



class AdminJobListView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        jobs = Job.objects.all().order_by("-created_on")
        serializer = JobListSerializer(jobs, many=True)
        return Response({"jobs": serializer.data}, status=200)
    
class AdminJobDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, job_id, *args, **kwargs):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        serializer = JobDetailSerializer(job)
        return Response(serializer.data, status=200)
    
    
class AdminUpdateJobStatusView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request, job_id, *args, **kwargs):
        new_status = request.data.get("active_status")

        if new_status not in ["pending", "approved", "rejected"]:
            return Response({"error": "Invalid status"}, status=400)

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        job.active_status = new_status
        job.save()
        NotificationModel.objects.create(
                user=job.created_by,
                title="Job Approval Notification",
                info=f"Admin {new_status} '{job.title}'"
            )
        
        return Response({"message": "Job status updated successfully"}, status=200)
    
    
    
    
# ================================================================================

class JobListView(APIView):
    def get(self, request, *args, **kwargs):
        jobs = Job.objects.filter(active_status="approved")
        serializer = JobListSerializer2(jobs, many=True)
        return Response({
            "jobs": serializer.data
        }, status=status.HTTP_200_OK)
        
        
        
class PhlebotomistAvailableListView(APIView):
    def get(self, request, *args, **kwargs):
        phlebotomists = PhlebotomistProfile.objects.filter(user__account_status="approved")

        available_phlebotomists = []
        
        for phlebotomist in phlebotomists:
            assigned_job = TempAssignedJob.objects.filter(assigned_to=phlebotomist.user, status='assigned').exists()
            status = "Busy" if assigned_job else "Available"

            phlebotomist_data = {
                "image": phlebotomist.image,
                "phlebotomist_id":phlebotomist.user.user_id,
                "full_name": phlebotomist.user.full_name,
                "location": phlebotomist.service_area,
                "years_of_experience": phlebotomist.years_of_experience,
                "status": status
            }
            available_phlebotomists.append(phlebotomist_data)

        return Response({
            "total_found": len(available_phlebotomists),
            "list": available_phlebotomists
        }, status=HTTP_200_OK)
        
        
class ViewPhlebotomistProfileView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        
        try:
            # Fetch the Phlebotomist profile based on user_id
            phlebotomist_profile = PhlebotomistProfile.objects.get(user__user_id=user_id)
        except PhlebotomistProfile.DoesNotExist:
            return Response({"error": "Phlebotomist not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the profile data
        serializer = PhlebotomistProfileSerializer(phlebotomist_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class AssignPhlebotomistToJobView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        job_id = request.data.get('job_id')
        phlebotomist_user_id = request.data.get('phlebotomist_user_id')
        assignment_start_time = request.data.get('assignment_start_time')
        assignment_end_time = request.data.get('assignment_end_time')

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            phlebotomist = User.objects.get(user_id=phlebotomist_user_id, role='phlebotomist')
        except User.DoesNotExist:
            return Response({"error": "Phlebotomist not found"}, status=status.HTTP_404_NOT_FOUND)

        existing_assignment = TempAssignedJob.objects.filter(assigned_to=phlebotomist, status="assigned").exists()
        if existing_assignment:
            return Response({"error": "Phlebotomist is already assigned to another job"}, status=status.HTTP_400_BAD_REQUEST)

        temp_assignment = TempAssignedJob.objects.create(
            job=job,
            assigned_to=phlebotomist,
            assigned_by=request.user,
            assignment_start_time=assignment_start_time,
            assignment_end_time=assignment_end_time,
            status='assigned'
        )
        
        NotificationModel.objects.create(
                user=job.created_by,
                title="New Assigned Job Notification",
                info=f"requested to accept '{job.title}' to {job.assigned_to}."
            )
        NotificationModel.objects.create(
                user=job.assigned_to,
                title="New Assigned Job Notification",
                info=f"assigned '{job.title}' by {job.created_by}."
            )
        
        return Response({
            "message": f"Phlebotomist {phlebotomist.full_name} successfully assigned to job {job.title}.",
            "assignment_id": temp_assignment.id
        }, status=status.HTTP_200_OK)
        
######################################################################################
class PendingBusinessOwnerProfileListView(APIView):
    def get(self, request, *args, **kwargs):
        pending_business_owners = CustomerUser.objects.filter(role='business_owner', account_status='pending')
        
        business_owner_data = []
        for user in pending_business_owners:
            profile = user.business_owner_profile
            created_ago = timezone.now() - user.date_joined
            days_ago = created_ago.days
            
            business_owner_data.append({
                'id':user.user_id,
                'business_name': profile.business_name if profile else None,
                'business_type': profile.business_type if profile else None,
                'user_full_name': user.full_name,
                'created': user.date_joined,
                'days_ago': days_ago,
                'account_status':user.is_active
            })
        
        return Response({
            "total_pending_business_owners": len(business_owner_data),
            "business_owners": business_owner_data
        }, status=status.HTTP_200_OK)
class BusinessOwnerProfileDetailView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user = CustomerUser.objects.get(user_id=user_id, role='business_owner', account_status='pending')
            profile = user.business_owner_profile
            
            business_owner_details = {
                'business_name': profile.business_name if profile else None,
                'business_type': profile.business_type if profile else None,
                'business_address': profile.business_address if profile else None,
                'contact_person_name': profile.contact_person_name if profile else None,
                'business_phone': profile.business_phone if profile else None,
                'business_license_number': profile.business_license_number if profile else None,
                'business_description': profile.business_description if profile else None,
                'business_license_document': profile.business_license_document.url if profile.business_license_document else None,
                'hourly_pay_rate': profile.hourly_pay_rate if profile else None,
                'preferred_job_types': profile.preferred_job_types if profile else None,
                'work_time': profile.work_time if profile else None,
                'weekly_schedule': profile.weekly_schedule if profile else None,
                'digital_sign': profile.digital_sign if profile else None,
                'agree': profile.agree if profile else None,
                'created': user.date_joined,
                'days_ago': (timezone.now() - user.date_joined).days
            }
            
            return Response(business_owner_details, status=status.HTTP_200_OK)
        except CustomerUser.DoesNotExist:
            return Response({"error": "Business Owner not found or not pending."}, status=status.HTTP_404_NOT_FOUND)
class AdminApproveBusinessOwnerProfileView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        action = request.data.get('action')  # 'approve' or 'reject'
        
        if action not in ['approve', 'reject']:
            return Response({"error": "Invalid action. Choose either 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomerUser.objects.get(user_id=user_id, role='business_owner', account_status='pending')
        except CustomerUser.DoesNotExist:
            return Response({"error": "Business Owner not found or not pending."}, status=status.HTTP_404_NOT_FOUND)
        
        if action == 'approve':
            user.account_status = 'approved'
        elif action == 'reject':
            user.account_status = 'rejected'
        
        user.save()
        
        NotificationModel.objects.create(
                user=user,
                title="Account Application Approved",
                info="approved by Admin."
            )

        return Response({
            "message": f"Business Owner account status updated to {user.account_status}."
        }, status=status.HTTP_200_OK)
        

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to anyone,
    but write/update access only to admins.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class PrivacyPolicyView(generics.RetrieveUpdateAPIView):
    queryset = PrivacyPolicy.objects.all()
    serializer_class = PrivacyPolicySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        return PrivacyPolicy.objects.first()

class TermsConditionsView(generics.RetrieveUpdateAPIView):
    queryset = TermsConditions.objects.all()
    serializer_class = TermsConditionsSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_object(self):
        return TermsConditions.objects.first()