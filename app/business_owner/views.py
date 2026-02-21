from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.business_owner.models import Job,TempAssignedJob,RequestForJob,CompletedAssignedJob,AcceptedAssignedJob
from app.business_owner.serializers import JobSerializer, JobPhlebotomistFilterSerializer,TempAssignedJobSerializer,RequestForJobSerializer,BusinessOwnerDashboardSerializer,UserProfileSerializer,CompletedAssignedJobSerializer
from datetime import timedelta,datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from app.phlebotomist.serializers import PhlebotomistListSerializer,PhlebotomistDetailSerializer
from app.accounts.models import NotificationModel
from rest_framework.permissions import IsAuthenticated
User = get_user_model()


class PostJobView(APIView):
    def post(self, request, *args, **kwargs):
        # Pass the request context to the serializer so it can access request.user
        serializer = JobSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Let the serializer handle the saving
            serializer.save()
            
            return Response({
                "message": "Job posted successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ViewBusinessOwnerJobsView(APIView):
    def get(self, request, *args, **kwargs):
        # Access filter_option from query parameters
        filter_option = request.query_params.get('filter_option', 'all')  # Default to 'all' if not provided

        # Apply filtering based on filter_option
        if filter_option == 'all':
            jobs = Job.objects.filter(created_by=request.user)
        elif filter_option == 'new':
            # Get jobs created in the last 24 hours
            jobs = Job.objects.filter(created_by=request.user, created_on__gte=timezone.now() - timedelta(hours=24))
        elif filter_option == 'assigned':
            jobs = Job.objects.filter(created_by=request.user, assigned=True)
        elif filter_option == 'completed':
            jobs = Job.objects.filter(created_by=request.user, completed=True)
        else:
            return Response({"error": "Invalid filter option"}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered job data
        job_serializer = JobSerializer(jobs, many=True)
        return Response(job_serializer.data, status=status.HTTP_200_OK)
###############################################################################




class PhlebotomistListView(APIView):
    def get(self, request, *args, **kwargs):
        # Filter users who are phlebotomists
        phlebotomists = User.objects.filter(role=User.PHLEBOTOMIST)

        # Serialize the filtered data
        serializer = PhlebotomistListSerializer(phlebotomists, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class PhlebotomistDetailView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            # Retrieve the phlebotomist by user_id
            phlebotomist = User.objects.get(user_id=user_id, role=User.PHLEBOTOMIST)

            # Serialize the phlebotomist details
            serializer = PhlebotomistDetailSerializer(phlebotomist)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Phlebotomist not found"}, status=status.HTTP_404_NOT_FOUND)




################################################################
class ViewPhlebotomistJobsView(APIView):
    def post(self, request, *args, **kwargs):
        filter_serializer = JobPhlebotomistFilterSerializer(data=request.data)
        if filter_serializer.is_valid():
            job_types = filter_serializer.validated_data['job_types']
            jobs = Job.objects.filter(job_types=job_types)
            job_serializer = JobSerializer(jobs, many=True)
            return Response(job_serializer.data, status=status.HTTP_200_OK)
        return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
##########################################################################################3



class TempAssignedJobListView(APIView):
    def get(self, request, *args, **kwargs):
        # Get all temporary assignments
        temp_assignments = TempAssignedJob.objects.filter(assigned_by=request.user)
        serializer = TempAssignedJobSerializer(temp_assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class TempAssignedJobCreateView(APIView):
    def post(self, request, *args, **kwargs):
        job_id = request.data.get("job")
        assigned_to_id = request.data.get("assigned_to")

        try:
            # Get the related Job and User (phlebotomist)
            job = Job.objects.get(id=job_id)
            assigned_to = User.objects.get(user_id=assigned_to_id)
            
            # Set start and end time based on the job's start and end time
            assignment_start_time = datetime.combine(job.date, job.start_time)
            assignment_end_time = datetime.combine(job.date, job.end_time)
            
            # Create the TempAssignedJob object with auto-filled fields
            temp_assigned_job = TempAssignedJob.objects.create(
                job=job,
                assigned_to=assigned_to,
                assigned_by=request.user,  # Automatically set to the current user
                assignment_start_time=assignment_start_time,
                assignment_end_time=assignment_end_time
            )
        
            NotificationModel.objects.create(
                user=request.user,
                title="New Job Assigned Request",
                info=f"Phlebotomist {assigned_to.full_name} has rejected the job '{temp_assigned_job.job.title}'."
            )
            
            NotificationModel.objects.create(
                user=assigned_to,
                title="New Job Assigned Request",
                info=f"assigned for '{temp_assigned_job.job.title}' job by {request.user.full_name}."
            )
            # Serialize and return the response
            serializer = TempAssignedJobSerializer(temp_assigned_job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Phlebotomist not found"}, status=status.HTTP_400_BAD_REQUEST)
        
#=====================================================================================================

class RequestJobView(APIView):
    def post(self, request, *args, **kwargs):
        job_id = request.query_params.get('job_id')

        if not job_id:
            return Response({"error": "job_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        
        existing_request = RequestForJob.objects.filter(job=job, requested_by=request.user).first()
        if existing_request:
            return Response({"error": "You have already applied for this job."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if job.assigned:
            return Response({"error": "Job is already assigned"}, status=status.HTTP_400_BAD_REQUEST)

        request_for_job = RequestForJob(
            job=job,
            requested_by=request.user,
            status="pending"
        )
        request_for_job.save()

        NotificationModel.objects.create(
                user=request.user,
                title="Apply For Job Request",
                info=f"request to assign for the job '{job.title}'."
            )
            
        NotificationModel.objects.create(
            user=job.created_by,
            title="New Application For Job Assig",
            info=f"Phlebotomist {request.user.full_name} for '{job.title}' job"
        )
        
        return Response({
            "message": "Job request sent successfully",
            "request_id": request_for_job.id
        }, status=status.HTTP_201_CREATED)


class ViewJobRequestsView(APIView):
    def get(self, request, *args, **kwargs):
        job_id = request.query_params.get('job_id')
        job = Job.objects.get(id=job_id)

        # Ensure that only the business owner can view job requests
        if job.created_by != request.user:
            return Response({"error": "You are not authorized to view this job's requests"}, status=status.HTTP_403_FORBIDDEN)

        requests = RequestForJob.objects.filter(job=job)
        serializer = RequestForJobSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
#=====================================================================================================================


class ApproveRejectRequestView(APIView):
    def post(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        status = request.data.get('status')  # 'approved' or 'rejected'

        try:
            request_for_job = RequestForJob.objects.get(id=request_id)
        except RequestForJob.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only the business owner can approve/reject the request
        if request_for_job.job.created_by != request.user:
            return Response({"error": "You are not authorized to approve/reject this request"}, status=status.HTTP_403_FORBIDDEN)

        # Update the status of the request
        if status == 'approved':
            request_for_job.status = 'assigned'
            request_for_job.job.assigned = True  # Mark job as assigned
            request_for_job.job.assigned_to = request_for_job.requested_by  # Assign job to phlebotomist
            request_for_job.job.save()
        else:
            request_for_job.status = 'rejected'

        request_for_job.save()

        return Response({
            "message": "Request status updated successfully",
            "status": request_for_job.status
        }, status=status.HTTP_200_OK)



class BusinessOwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "business_owner":
            return Response({"error": "You are not authorized to view this dashboard."}, status=403)

        serializer = BusinessOwnerDashboardSerializer(request.user)
        return Response(serializer.data, status=200)
    


class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user profile of the currently logged-in user
        try:
            user_profile = User.objects.get(user_id=request.user.user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Serialize the data
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)


class CompleteJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id, *args, **kwargs):
        try:
            # Get the AcceptedAssignedJob instance
            accepted_job = AcceptedAssignedJob.objects.get(id=appointment_id)

            # Ensure the job is assigned to the current user and is active
            if accepted_job.assigned_to != request.user or not accepted_job.is_active:
                return Response({"error": "Job is either not assigned to you or is already completed."}, status=status.HTTP_400_BAD_REQUEST)

            # Update the AcceptedAssignedJob to mark as completed
            accepted_job.completed = True
            accepted_job.is_active = False
            accepted_job.save()

            # Create a new CompletedAssignedJob instance
            completed_job = CompletedAssignedJob.objects.create(
                job=accepted_job.job,
                completed_by=request.user,
                assigned_by=accepted_job.assigned_by,
                payment_status=True,  # Assuming the payment is marked as complete
            )

            # Serialize the completed job
            completed_job_serializer = CompletedAssignedJobSerializer(completed_job)

            return Response({
                "message": "Job marked as completed successfully",
                "completed_job": completed_job_serializer.data
            }, status=status.HTTP_200_OK)

        except AcceptedAssignedJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)