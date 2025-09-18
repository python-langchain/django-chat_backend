from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "nickname"]


class MessageSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "content", "metadata", "created_at"]
        read_only_fields = ["id", "sender", "created_at"]


class ChatSerializer(serializers.ModelSerializer):
    participants = PublicUserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "participants", "created_at", "updated_at", "last_message"]

    def get_last_message(self, obj: Chat):
        m = obj.messages.order_by("-created_at").first()
        return MessageSerializer(m).data if m else None
