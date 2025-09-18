from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns

# HTTP is standard Django; WebSocket uses custom JWT auth inside consumer
application = ProtocolTypeRouter(
    {"http": get_asgi_application(), "websocket": URLRouter(websocket_urlpatterns)}
)
