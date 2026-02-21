from django.urls import path
from app.dashboard.views import UserManagementListView,UserProfileView,UpdateAccountStatusView,DashboardDataView,PendingPhlebotomistListView,PendingPhlebotomistDetailView,AdminApproveRejectPhlebotomistView,AdminJobDetailView,AdminJobListView,AdminUpdateJobStatusView,JobListView,PhlebotomistAvailableListView,ViewPhlebotomistProfileView,AssignPhlebotomistToJobView,PendingBusinessOwnerProfileListView,BusinessOwnerProfileDetailView,AdminApproveBusinessOwnerProfileView,PrivacyPolicyView,TermsConditionsView

urlpatterns = [
    path("data/",DashboardDataView.as_view()),
    #
    path('users/list/', UserManagementListView.as_view(), name='user_management_list'),
    path('users/<str:user_id>/profile/', UserProfileView.as_view(), name='view_user_profile'),
    path('users/<str:user_id>/update-status/', UpdateAccountStatusView.as_view(), name='update_account_status'),
    #
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('terms-and-conditions/', TermsConditionsView.as_view(), name='terms-and-conditions'),
    #
    path("jobs/list/", AdminJobListView.as_view(), name="admin_job_list"),
    path("jobs/<str:job_id>/detail/", AdminJobDetailView.as_view(), name="admin_job_detail"),
    path("jobs/<str:job_id>/update-status/", AdminUpdateJobStatusView.as_view(), name="admin_job_update_status"),
    #
    path("phlebotomists/pending/list/",PendingPhlebotomistListView.as_view(),name="Pending List"),
    path("phlebotomists/pending/<int:user_id>/profile/view/",PendingPhlebotomistDetailView.as_view()),
    path("phlebotomists/profile/approve-reject/",AdminApproveRejectPhlebotomistView.as_view()),
    #
    path('business-owners/pending/list/', PendingBusinessOwnerProfileListView.as_view(), name='pending_business_owner_list'),
    path('business-owners/pending/<str:user_id>/profile/view/', BusinessOwnerProfileDetailView.as_view(), name='business_owner_detail'),
    path('business-owners/profile/approve-reject/', AdminApproveBusinessOwnerProfileView.as_view(), name='approve_reject_business_owner'),

    #
    path('jobs/matching/list/', JobListView.as_view(), name='job_list'),
    path('jobs/matching/phlebotomists/available/', PhlebotomistAvailableListView.as_view(), name='phlebotomist_available_list'), # available astecena
    path('jobs/matching/phlebotomist/<str:user_id>/profile/', ViewPhlebotomistProfileView.as_view(), name='phlebotomist_profile'),
    path('jobs/matching/phlebotomist/assign/', AssignPhlebotomistToJobView.as_view(), name='assign_phlebotomist_to_job'),
    
]

