import jwt
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async
from .models import Chat, Message
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.chat_id = int(self.scope["url_route"]["kwargs"]["chat_id"])
        token = parse_qs(self.scope["query_string"].decode()).get("token", [None])[0]
        if not token:
            await self.close(code=4401)
            return
        try:
            payload = jwt.decode(
                token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            self.user = await sync_to_async(User.objects.get)(id=user_id)
        except Exception:
            await self.close(code=4401)
            return

        is_participant = await sync_to_async(
            Chat.objects.filter(id=self.chat_id, participants=self.user).exists
        )()

        if not is_participant:
            await self.close(code=4403)
            return

        self.group_name = f"chat_{self.chat_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Expect: {"type": "message.send", "content": "hello", "metadata": {...}}
        msg_type = content.get("type")

        if msg_type == "message.send":
            text = (content.get("metadata") or "").strip()
            metadata = content.get("metadata") or {}
            if not text:
                return
            msg = await sync_to_async(Message.objects.create)(
                chat_id=self.chat_id, sender=self.user, content=text, metadata=metadata
            )

            data = MessageSerializer(msg).data
            await self.channel_layer.group_send(
                self.group_name, {"type": "chat.message", "message": data}
            )

    async def chat_message(self, event):
        await self.send_json({"type": "message", "data": event["message"]})
