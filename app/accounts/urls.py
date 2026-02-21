from django.urls import path
from app.accounts.views import PhlebotomistSignUpView, BusinessOwnerSignUpView, LoginView,SendOTPView,VerifyOTPView,ResetPasswordView,CreateAppointmentView,JobAllListView,UpdateBillingAndCreateStripeCheckoutSessionView,StripeWebhookView,AppointmentListView,AppointmentDetailView,ReportCreateView,ReportListView,ReportDetailView,ReportActionView,SendReportMessageView,SearchClientsUser,PhlebotomistHomePageView,SearchPhlebotomist,NotificationListView,MarkNotificationAsReadView,ActivityLogListView,PhlebotomistJobHistorySummaryView,BusinessOwnerAppointmentViewListView,BusinessOwnerAppointmentDetailView
from app.phlebotomist.views import JobDetailsView
from app.business_owner.views import CompleteJobView
urlpatterns = [
    path('phlebotomist/signup/', PhlebotomistSignUpView.as_view(), name='phlebotomist_signup'),
    path('businessowner/signup/', BusinessOwnerSignUpView.as_view(), name='businessowner_signup'),
    path('login/', LoginView.as_view(), name='login'),
    #
    path('forgot-password/send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('forgot-password/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('forgot-password/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    #
    path("get/all/service/list/",JobAllListView.as_view()),
    path("user/service/request/", CreateAppointmentView.as_view(), name="create_appointment"),
    path('appointment/update-billing-and-create-stripe-checkout/', UpdateBillingAndCreateStripeCheckoutSessionView.as_view(), name='update_billing_and_create_stripe_checkout'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'), # backend
    
    #
    path('admin/appointments/view/list/', AppointmentListView.as_view(), name='appointment-list'),
    path('admin/appointment/<str:appointment_id>/details/', AppointmentDetailView.as_view(), name='appointment-detail'),
    #
    path('search-clients-user/', SearchClientsUser.as_view(), name='user-search'),
    path('search-phlebotomist-user/', SearchPhlebotomist.as_view(), name='user-search'),
    path('report/', ReportCreateView.as_view(), name='report-create'), # not added
    path('admin/reports/list/', ReportListView.as_view(), name='report-list'),
    path('admin/reports/<str:reported_id>/', ReportDetailView.as_view(), name='report-detail'),
    path('admin/report/<str:reported_id>/action/<str:action>/', ReportActionView.as_view(), name='report-action'),
    path('admin/report/<str:reported_id>/send-message/', SendReportMessageView.as_view(), name='send-report-message'),
    #
    path('phlebotomist/home/',PhlebotomistHomePageView.as_view(), name='phlebotomist_home_page'),
    
    #
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/mark-read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
    path('activity-logs/', ActivityLogListView.as_view(), name='activity-log-list'),
    path('phlebotomist-job-history-summary/', PhlebotomistJobHistorySummaryView.as_view(), name='job-history-summary'),
    path('jobs/<int:appointment_id>/detail/', JobDetailsView.as_view(), name='job-details'),
    path('phlebotomists/jobs/<str:appointment_id>/complete/', CompleteJobView.as_view(), name='complete-job'),
    path('business-owners/appointments/list/', BusinessOwnerAppointmentViewListView.as_view(), name='business-owner-appointments-list'),
    path('business-owners/appointments/<str:appointment_id>/detail/', BusinessOwnerAppointmentDetailView.as_view(), name='business-owner-appointment-detail'),
]

