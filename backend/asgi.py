import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()  # <-- setup first

from channels.routing import ProtocolTypeRouter, URLRouter
from main.middleware import JWTAuthMiddleware  # now safe to import
from main import routing as routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
     URLRouter(
            routing.websocket_urlpatterns 
        )
    ),
})

