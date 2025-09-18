from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from .utils import pair_key_for_users

User = settings.AUTH_USER_MODEL


class Chat(models.Model):
    pair_key = models.CharField(max_length=64, unique=True, db_index=True)
    participants = models.ManyToManyField(User, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_or_create_1to1(cls, user_a_id: int, user_b_id: int):
        key = pair_key_for_users(user_a_id, user_b_id)
        chat, created = cls.objects.get_or_create(pair_key=key)

        if created:
            chat.participants.set([user_a_id, user_b_id])

        return chat, created

    def __str__(self):
        return f"Chat<{self.id}>"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_sent"
    )
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # JSONB
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["chat", "created_at"], name="chat_created_idx"),
            GinIndex(fields=["metadata"], name="message_meta_gin"),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"Msg<{self.id}> in Chat<{self.chat_id}> by {self.sender_id}"
