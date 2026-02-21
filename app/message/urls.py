from django.urls import path
from .views import SendMessageView, ChatHistoryView,InappropriateMessageReportListView,InappropriateMessageReportDetailView,AdminActionView,ChatListView

urlpatterns = [
    path('send-message/', SendMessageView.as_view(), name='send-message'),
    path('chat-history/', ChatHistoryView.as_view(), name='chat-history'),
    path('chat/list/', ChatListView.as_view(), name='chat-list'),
    #
    path(
        'admin/reports/inappropriate/',InappropriateMessageReportListView.as_view(),name='inappropriate-report-list'
    ),

    path(
        'admin/reports/inappropriate/<str:report_id>/',
        InappropriateMessageReportDetailView.as_view(),
        name='inappropriate-report-detail'
    ),
    path("admin/report/action/",AdminActionView.as_view(),name="action")
]


