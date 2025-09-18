"""
WebSocket routing configuration for chat application.

Defines WebSocket URL patterns for real-time chat functionality.
These routes handle WebSocket connections for live messaging within chat rooms.
"""

from django.urls import re_path
from .consumers import ChatConsumer

# WebSocket URL patterns for chat functionality
websocket_urlpatterns = [
    # WebSocket route for connecting to a specific chat room
    # Pattern: ws/chats/{chat_id}/
    # Connects clients to real-time messaging for the specified chat
    re_path(r"^ws/chats/(?P<chat_id>\d+)/$", ChatConsumer.as_asgi())
]
