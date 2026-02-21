from django.urls import path
from app.business_owner.views import ViewPhlebotomistJobsView,RequestJobView
from app.phlebotomist.views import JobListView,JobDetailView,TempAssignedJobListView,PhlebotomistProfilePartialUpdateView,AcceptRejectJobView,JobDetailsView
from app.accounts.views import PhlebotomistProfileView
urlpatterns = [
    path('phlebotomist-profiles/update/', PhlebotomistProfilePartialUpdateView.as_view(), name='phlebotomist-profile-multi-update'),
    #
    path('jobs/phlebotomist/view/', ViewPhlebotomistJobsView.as_view(), name='view_phlebotomist_jobs'), #not addded
    #
    path('jobs/available/list/', JobListView.as_view(), name='job-list'),
    path('jobs/<job_id>/detail/', JobDetailView.as_view(), name='job-detail'),
    #
    path('assigned-job-list/', TempAssignedJobListView.as_view(), name='assigned-phlebotomists'),
    #
    path('request-job/', RequestJobView.as_view(), name='request-job'),
    path('jobs/accept-reject/', AcceptRejectJobView.as_view(), name='accept-reject-job'),
    #
    path('phlebotomist/profile/', PhlebotomistProfileView.as_view(), name='phlebotomist-profile'),
    path('jobs/<int:appointment_id>/detail/', JobDetailsView.as_view(), name='job-details'),
]
