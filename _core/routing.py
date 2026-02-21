from django.urls import re_path
from app.message import consumers

websocket_urlpatterns = [
    # Updated regex to include the trailing slash and fix the route matching
    re_path(r'ws/messages/(?P<receiver_id>\d+)/$', consumers.MessageConsumer.as_asgi()),
]
