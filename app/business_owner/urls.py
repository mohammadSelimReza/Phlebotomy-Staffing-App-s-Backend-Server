from django.urls import path
from app.business_owner.views import PostJobView, ViewBusinessOwnerJobsView,PhlebotomistListView,PhlebotomistDetailView,TempAssignedJobCreateView,TempAssignedJobListView,BusinessOwnerDashboardView,GetProfileView
from app.accounts.views import BusinessOwnerAppointmentListView,AppointmentDetailViewBusiness

urlpatterns = [
    path('job/post/', PostJobView.as_view(), name='post_job'),
    path('jobs/businessowner/view/', ViewBusinessOwnerJobsView.as_view(), name='view_businessowner_jobs'),
    #
    path('phlebotomists/list/', PhlebotomistListView.as_view(), name='phlebotomist-list'),
    path('phlebotomist/<user_id>/detail/', PhlebotomistDetailView.as_view(), name='phlebotomist-detail'),
    #
    path('temp-assignments/create/', TempAssignedJobCreateView.as_view(), name='temp-assigned-job-create'),
    path('assigned-phlebotomists/', TempAssignedJobListView.as_view(), name='assigned-phlebotomists'),
    path('dashboard/', BusinessOwnerDashboardView.as_view(), name='business-owner-dashboard'),
    path('appointments/list/', BusinessOwnerAppointmentListView.as_view(), name='appointment-list'), 
    path('appointments/<str:appointment_id>/', AppointmentDetailViewBusiness.as_view(), name='appointment-detail'),
    path('profile/', GetProfileView.as_view(), name='get-profile'),
    
]
