"""
Chat application models for handling one-to-one conversations and messages.

This module defines the core data models for the chat system:
- Chat: Represents a conversation between two users
- Message: Individual messages within a chat conversation
"""

from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from .utils import pair_key_for_users

# Reference to the user model defined in settings
User = settings.AUTH_USER_MODEL


class Chat(models.Model):
    """
    Model representing a chat conversation between two users.
    
    Uses a unique pair_key to ensure only one chat exists between any two users,
    preventing duplicate conversations.
    """
    # Unique identifier for the chat pair (generated from user IDs)
    pair_key = models.CharField(max_length=64, unique=True, db_index=True)
    
    # Many-to-many relationship with users (should be exactly 2 participants)
    participants = models.ManyToManyField(User, related_name="chats")
    
    # Timestamps for tracking chat creation and last activity
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_or_create_1to1(cls, user_a_id: int, user_b_id: int):
        """
        Get or create a one-to-one chat between two users.
        
        Args:
            user_a_id (int): ID of the first user
            user_b_id (int): ID of the second user
            
        Returns:
            tuple: (Chat instance, created boolean)
        """
        # Generate a unique key for this user pair
        key = pair_key_for_users(user_a_id, user_b_id)
        chat, created = cls.objects.get_or_create(pair_key=key)

        # If this is a new chat, add both users as participants
        if created:
            chat.participants.set([user_a_id, user_b_id])

        return chat, created

    def __str__(self):
        """String representation of the chat."""
        return f"Chat<{self.id}>"


class Message(models.Model):
    """
    Model representing an individual message within a chat.
    
    Each message belongs to a chat and has a sender, content, and optional metadata.
    """
    # Foreign key to the chat this message belongs to
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    
    # Foreign key to the user who sent this message
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_sent"
    )
    
    # The actual message content
    content = models.TextField()
    
    # Optional JSON metadata for storing additional message information
    metadata = models.JSONField(default=dict, blank=True)  # JSONB in PostgreSQL
    
    # Timestamp for when the message was created (indexed for efficient ordering)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        """Meta configuration for the Message model."""
        indexes = [
            # Composite index for efficient querying of messages by chat and time
            models.Index(fields=["chat", "created_at"], name="chat_created_idx"),
            # GIN index for efficient JSON metadata queries
            GinIndex(fields=["metadata"], name="message_meta_gin"),
        ]
        # Default ordering by creation time (oldest first)
        ordering = ["created_at"]

    def __str__(self):
        """String representation of the message."""
        return f"Msg<{self.id}> in Chat<{self.chat_id}> by {self.sender_id}"
