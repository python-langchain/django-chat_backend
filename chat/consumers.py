"""
WebSocket consumers for real-time chat functionality.

This module provides WebSocket support for live cha        if msg_type == "message.send":
            # Extract message content and metadata
            text = (content.get("content") or "").strip()  # Fixed: was getting "metadata" instead of "content"
            metadata = content.get("metadata") or {}atures using Django Channels.
Handles user authentication, chat room management, and real-time message broadcasting.
"""

import jwt
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async
from .models import Chat, Message
from .serializers import MessageSerializer

# Get the user model configured in Django settings
User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat communication.
    
    Manages individual chat room connections, user authentication via JWT tokens,
    and real-time message broadcasting to all connected participants.
    """
    
    async def connect(self):
        """
        Handle new WebSocket connections.
        
        Authenticates the user via JWT token, verifies chat participation,
        and adds the connection to the appropriate chat group.
        
        Connection will be closed with specific codes if:
        - 4401: Authentication failed (missing/invalid token)
        - 4403: User is not a participant in the requested chat
        """
        # Extract chat ID from the URL route
        self.chat_id = int(self.scope["url_route"]["kwargs"]["chat_id"])
        
        # Extract JWT token from query parameters
        token = parse_qs(self.scope["query_string"].decode()).get("token", [None])[0]
        if not token:
            await self.close(code=4401)  # Unauthorized
            return
            
        try:
            # Decode and validate the JWT token
            payload = jwt.decode(
                token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            # Get the user from the database
            self.user = await sync_to_async(User.objects.get)(id=user_id)
        except Exception:
            # Token is invalid or user doesn't exist
            await self.close(code=4401)  # Unauthorized
            return

        # Verify the user is a participant in this chat
        is_participant = await sync_to_async(
            Chat.objects.filter(id=self.chat_id, participants=self.user).exists
        )()

        if not is_participant:
            await self.close(code=4403)  # Forbidden
            return

        # Create a unique group name for this chat
        self.group_name = f"chat_{self.chat_id}"

        # Add this connection to the chat group for broadcasting
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnections.
        
        Removes the connection from the chat group to prevent messages
        being sent to a closed connection.
        
        Args:
            close_code: WebSocket close code indicating reason for disconnection
        """
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        """
        Handle incoming JSON messages from the client.
        
        Processes different message types and performs corresponding actions.
        Currently supports sending new messages to the chat.
        
        Expected message format:
        {
            "type": "message.send",
            "content": "message text",
            "metadata": {...}  // optional
        }
        
        Args:
            content: Parsed JSON content from the client
        """
        msg_type = content.get("type")

        if msg_type == "message.send":
            # Extract message content and metadata
            text = (content.get("content") or "").strip()
            metadata = content.get("metadata") or {}
            
            # Don't process empty messages
            if not text:
                return
                
            # Create the message in the database
            msg = await sync_to_async(Message.objects.create)(
                chat_id=self.chat_id, 
                sender=self.user, 
                content=text, 
                metadata=metadata
            )

            # Serialize the message for broadcasting
            data = MessageSerializer(msg).data
            
            # Broadcast the new message to all connections in this chat group
            await self.channel_layer.group_send(
                self.group_name, 
                {"type": "chat.message", "message": data}
            )

    async def chat_message(self, event):
        """
        Handle messages sent to the chat group.
        
        This method is called when a message is broadcast to the group
        (either from this consumer or another one in the same chat).
        
        Args:
            event: Dictionary containing the message data to send
        """
        # Send the message to the WebSocket client
        await self.send_json({"type": "message", "data": event["message"]})
