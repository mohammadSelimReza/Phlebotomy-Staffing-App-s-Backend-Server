from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.business_owner.serializers import JobDetailsViewSerializser,TempAssignedJobSerializer,JobListForPhlebotomistSerializer
from app.business_owner.models import Job,TempAssignedJob
from app.accounts.models_profile import PhlebotomistProfile
from app.accounts.serializer_phlebotomist.serializers import PhlebotomistProfileSerializer
from rest_framework.permissions import IsAuthenticated
from app.accounts.models import NotificationModel,ActivityLog
from app.phlebotomist.serializers import AcceptedAssignedJobSerializer,AcceptedAssignedJob

class PhlebotomistProfilePartialUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can update their profile
    
    def patch(self, request, *args, **kwargs):
        # Use the authenticated user (request.user) instead of user_id from URL
        user = request.user
        
        try:
            # Retrieve the phlebotomist profile for the authenticated user
            profile = PhlebotomistProfile.objects.get(user=user)

            # Use the serializer to update the profile
            serializer = PhlebotomistProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()  # Save the updated profile
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PhlebotomistProfile.DoesNotExist:
            return Response({"error": "Phlebotomist profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
class JobListView(APIView):
    def get(self, request, *args, **kwargs):
        jobs = Job.objects.filter(assigned=False, completed=False)
        
        # Apply additional filtering based on job type (urgent, full day, part time, or all)
        job_type = request.query_params.get('job_type', 'all')
        if job_type != 'all':
            jobs = jobs.filter(job_types=job_type)

        serializer = JobListForPhlebotomistSerializer(jobs,context={'request': request}, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class JobDetailView(APIView):
    def get(self, request, job_id, *args, **kwargs):
        try:
            # Get the job by id
            job = Job.objects.get(id=job_id)

            # Serialize the job detail
            serializer = JobDetailsViewSerializser(job)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
class TempAssignedJobListView(APIView):
    def get(self, request, *args, **kwargs):
        temp_assignments = TempAssignedJob.objects.filter(assigned_to=request.user)
        serializer = TempAssignedJobSerializer(temp_assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AcceptRejectJobView(APIView):
    def post(self, request, *args, **kwargs):
        temp_assigned_job_id = request.data.get('temp_assigned_job_id')
        action = request.data.get('action')

        if action not in ['accept', 'reject']:
            return Response({"error": "Invalid action, must be either 'accept' or 'reject'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            temp_assigned_job = TempAssignedJob.objects.get(id=temp_assigned_job_id, assigned_to=request.user)
        except TempAssignedJob.DoesNotExist:
            return Response({"error": "Job assignment not found or you're not assigned to this job."}, status=status.HTTP_404_NOT_FOUND)

        if action == "accept":
            temp_assigned_job.status = 'assigned'
            temp_assigned_job.is_accepted = True
            temp_assigned_job.job.assigned = True
            
            NotificationModel.objects.create(
                user=request.user,
                title="Job Accepted",
                info=f"accepted the job '{temp_assigned_job.job.title}'."
            )

            ActivityLog.objects.create(
                user=request.user,
                title="Job Accepted",
                info=f"accepted the job '{temp_assigned_job.job.title}'."
            )

            
        elif action == "reject":
            temp_assigned_job.status = 'cancelled'
            temp_assigned_job.is_accepted = False

            
            NotificationModel.objects.create(
                user=temp_assigned_job.job.created_by,
                title="Job Rejected",
                info=f"rejected the job '{temp_assigned_job.job.title}'."
            )

            ActivityLog.objects.create(
                user=request.user,
                title="Job Rejected",
                info=f"rejected the job '{temp_assigned_job.job.title}'."
            )
        temp_assigned_job.save()

        return Response({
            "message": f"Job has been {action}ed successfully.",
            "status": temp_assigned_job.status
        }, status=status.HTTP_200_OK)
        
        
class CompleteJobView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the temp_assigned_job_id and ensure the Phlebotomist is the one completing the job
        temp_assigned_job_id = request.data.get('temp_assigned_job_id')

        if not temp_assigned_job_id:
            return Response({"error": "temp_assigned_job_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            temp_assigned_job = TempAssignedJob.objects.get(id=temp_assigned_job_id, assigned_to=request.user)
        except TempAssignedJob.DoesNotExist:
            return Response({"error": "Job assignment not found or you are not assigned to this job"}, status=status.HTTP_404_NOT_FOUND)

        if temp_assigned_job.status == 'completed':
            return Response({"message": "Job has already been completed."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark the job as completed in TempAssignedJob
        temp_assigned_job.status = 'completed'
        temp_assigned_job.is_accepted = True
        temp_assigned_job.save()

        # Update the job status to completed if all temp assignments are completed
        job = temp_assigned_job.job
        job.completed = True
        job.completed_by = request.user
        job.save()

        # Create Notification for the Business Owner (job creator)
        NotificationModel.objects.create(
            user=job.created_by,  # The business owner is notified
            title="Job Completed",
            info=f"The Phlebotomist {request.user.full_name} has completed the job '{job.title}'."
        )

        # Optionally, create an Activity Log entry for the completion
        ActivityLog.objects.create(
            user=request.user,
            title=f"Completed Job: {job.title}",
            info=f"Phlebotomist {request.user.full_name} completed the job."
        )

        return Response({
            "message": "Job marked as completed successfully.",
            "job_id": job.id,
            "status": temp_assigned_job.status
        }, status=status.HTTP_200_OK)
        
        
class JobDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id, *args, **kwargs):
        try:
            print(appointment_id)  # Check if appointment_id is being passed correctly
            job_details = AcceptedAssignedJob.objects.get(id=appointment_id)
            print(job_details)  # Check if the job is found
        except AcceptedAssignedJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AcceptedAssignedJobSerializer(job_details)

        return Response(serializer.data, status=status.HTTP_200_OK)