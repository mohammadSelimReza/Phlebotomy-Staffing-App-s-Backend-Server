import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the default Django settings module for the 'django' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_core.settings')

# Initialize the Django ASGI application to ensure the app registry is populated
django_asgi_app = get_asgi_application()

# Import your WebSocket consumers
from app.message.consumers import MessageConsumer  # noqa: E402

# Routing configuration
application = ProtocolTypeRouter({
    # HTTP connections go to Django's standard ASGI application
    "http": django_asgi_app,
    
    # WebSocket connections go through AllowedHostsOriginValidator, AuthMiddlewareStack, and URLRouter
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # WebSocket path (matching the updated regex)
                path('ws/messages/<receiver_id>/', MessageConsumer.as_asgi()),
            ])
        )
    ),
})
