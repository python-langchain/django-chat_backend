"""
Serializers for chat application API responses.

This module defines DRF serializers for converting model instances to/from JSON:
- PublicUserSerializer: Safe user information for API responses
- MessageSerializer: Message data with sender information
- ChatSerializer: Chat data with participants and last message
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat, Message

# Get the user model configured in Django settings
User = get_user_model()


class PublicUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information that's safe to expose publicly.
    
    Only includes non-sensitive user fields that can be shared with other users
    in chat contexts (excludes password, email verification status, etc.).
    """
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "nickname"]


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages.
    
    Includes read-only sender information using PublicUserSerializer to provide
    context about who sent each message without exposing sensitive data.
    """
    # Include sender details as read-only nested data
    sender = PublicUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "content", "metadata", "created_at"]
        # These fields are automatically managed and shouldn't be set via API
        read_only_fields = ["id", "sender", "created_at"]


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for chat conversations.
    
    Includes all participants and the most recent message to provide
    sufficient context for chat list displays.
    """
    # Include all participants' public information
    participants = PublicUserSerializer(many=True, read_only=True)
    
    # Include the most recent message for preview purposes
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "participants", "created_at", "updated_at", "last_message"]

    def get_last_message(self, obj: Chat):
        """
        Get the most recent message in this chat.
        
        Args:
            obj: Chat instance
            
        Returns:
            dict or None: Serialized message data or None if no messages exist
        """
        # Get the most recent message from this chat
        m = obj.messages.order_by("-created_at").first()
        return MessageSerializer(m).data if m else None
