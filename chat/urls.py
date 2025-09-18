"""
URL routing configuration for chat application REST API endpoints.

Defines the URL patterns for HTTP-based chat functionality:
- POST /start/ - Start a new chat with another user
- GET /chats/ - List all chats for the authenticated user  
- GET/POST /chats/<id>/messages/ - Retrieve or send messages in a specific chat
"""

from django.urls import path
from . import views

urlpatterns = [
    # Endpoint to initiate a new chat conversation with another user
    path("start/", views.start_chat, name="start_chat"),
    
    # Endpoint to list all chats for the current user
    path("chats/", views.list_chats, name="list_chats"),
    
    # Endpoint to handle messages within a specific chat
    # Supports both retrieving messages (GET) and sending new messages (POST)
    path("chats/<int:chat_id>/messages/", views.messages_view, name="messages"),
]
