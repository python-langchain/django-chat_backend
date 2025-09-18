from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from .utils import pair_key_for_users

User = get_user_model()


# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_chat(request):
    other_id = request.data.get("user_id")

    if not other_id:
        return Response({"detail": "user_id is required"}, status=400)

    if int(other_id) == request.user.id:
        return Response({"detail": "Cannot start chat with yourself"}, status=400)

    get_object_or_404(User, id=other_id)

    chat, created = Chat.get_or_create_1to1(request.user.id, other_id)

    return Response(
        ChatSerializer(chat).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_chats(request):
    chats = Chat.objects.filter(participants=request.user).prefetch_related(
        "participants"
    )
    data = ChatSerializer(chats.order_by("-updated_at"), many=True).data

    return Response(data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def messages_view(request, chat_id: int):
    chat = get_object_or_404(Chat, id=chat_id)

    if not chat.participants.filter(id=request.user.id).exists():
        return Response({"detail": "Not a participant"}, status=403)

    if request.method == "POST":
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            msg = Message.objects.create(
                chat=chat,
                sender=request.user,
                content=serializer.validated_data["content"],
                metadata=serializer.validated_data.get("metadata", {}),
            )
            # Touch chat updated_at for ordering
            Chat.objects.filter(id=chat.id).update()

            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{chat.id}",
                {
                    "type": "chat.message",
                    "message": MessageSerializer(msg).data,
                },
            )

            return Response(MessageSerializer(msg).data, status=201)
        return Response(serializer.errors, status=400)

    qs = chat.messages.select_related("sender").order_by("-created_at")

    from rest_framework.pagination import PageNumberPagination

    paginator = PageNumberPagination()
    paginator.page_size = int(request.query_params.get("page_size", 25))

    result_page = paginator.paginate_queryset(qs, request)
    data = MessageSerializer(result_page, many=True).data

    data = list(reversed(data))
    return paginator.get_paginated_response(data)
