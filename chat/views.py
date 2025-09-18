"""
API views for chat functionality.

This module provides REST API endpoints for:
- Starting new chat conversations
- Listing user's chats
- Retrieving and sending messages within a chat
"""

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

# Get the user model configured in Django settings
User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_chat(request):
    """
    API endpoint to start a new chat with another user.
    
    Creates a new chat conversation between the authenticated user and 
    the specified user, or returns existing chat if one already exists.
    
    Expected POST data:
        - user_id: ID of the user to start chat with
        
    Returns:
        - 201: New chat created
        - 200: Existing chat returned
        - 400: Invalid request (missing user_id, self-chat attempt)
        - 404: Target user not found
    """
    other_id = request.data.get("user_id")

    # Validate that user_id is provided
    if not other_id:
        return Response({"detail": "user_id is required"}, status=400)

    # Prevent users from starting chat with themselves
    if int(other_id) == request.user.id:
        return Response({"detail": "Cannot start chat with yourself"}, status=400)

    # Ensure the target user exists
    get_object_or_404(User, id=other_id)

    # Get or create a one-to-one chat between the users
    chat, created = Chat.get_or_create_1to1(request.user.id, other_id)

    return Response(
        ChatSerializer(chat).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_chats(request):
    """
    API endpoint to list all chats for the authenticated user.
    
    Returns all chat conversations where the user is a participant,
    ordered by most recently updated first.
    
    Returns:
        - 200: List of user's chats with participants and last message
    """
    # Get all chats where the user is a participant
    chats = Chat.objects.filter(participants=request.user).prefetch_related(
        "participants"
    )
    
    # Serialize the chats ordered by most recent activity
    data = ChatSerializer(chats.order_by("-updated_at"), many=True).data

    return Response(data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def messages_view(request, chat_id: int):
    """
    API endpoint to handle messages within a specific chat.
    
    GET: Retrieve paginated messages from the chat (newest first, then reversed)
    POST: Send a new message to the chat and broadcast it via WebSocket
    
    Args:
        chat_id: ID of the chat to retrieve/send messages for
        
    GET Parameters:
        - page_size: Number of messages per page (default: 25)
        
    POST Data:
        - content: Message content (required)
        - metadata: Optional JSON metadata
        
    Returns:
        GET - 200: Paginated list of messages
        POST - 201: Created message data
        - 400: Invalid request data
        - 403: User not a participant in the chat
        - 404: Chat not found
    """
    # Get the chat or return 404 if not found
    chat = get_object_or_404(Chat, id=chat_id)

    # Verify the user is a participant in this chat
    if not chat.participants.filter(id=request.user.id).exists():
        return Response({"detail": "Not a participant"}, status=403)

    if request.method == "POST":
        # Handle sending a new message
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            # Create the new message
            msg = Message.objects.create(
                chat=chat,
                sender=request.user,
                content=serializer.validated_data["content"],
                metadata=serializer.validated_data.get("metadata", {}),
            )
            
            # Update chat's updated_at timestamp for proper ordering
            Chat.objects.filter(id=chat.id).update()

            # Broadcast the new message to all connected WebSocket clients
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

    # Handle GET request - retrieve paginated messages
    # Get messages ordered by newest first, with sender information
    qs = chat.messages.select_related("sender").order_by("-created_at")

    # Set up pagination
    from rest_framework.pagination import PageNumberPagination

    paginator = PageNumberPagination()
    paginator.page_size = int(request.query_params.get("page_size", 25))

    # Get the requested page of messages
    result_page = paginator.paginate_queryset(qs, request)
    data = MessageSerializer(result_page, many=True).data

    # Reverse the order so oldest messages appear first in the response
    data = list(reversed(data))
    return paginator.get_paginated_response(data)
