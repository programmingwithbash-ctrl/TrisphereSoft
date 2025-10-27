# store/consumers.py
import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode
from jwt.exceptions import InvalidTokenError

from .models import Message  # <-- your Message model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    # Map user IDs to channel names for active WebSocket connections
    active_users = {}  # {str(user_id): channel_name}

    async def connect(self):
        # parse token from query string
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get("token", [None])[0]

        if not token:
            await self.close()
            return

        # decode JWT to get user_id
        try:
            payload = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                await self.close()
                return
            self.user = await self.get_user(user_id)
            if not self.user:
                await self.close()
                return
        except InvalidTokenError:
            await self.close()
            return
        except Exception:
            await self.close()
            return

        # register connection
        ChatConsumer.active_users[str(self.user.id)] = self.channel_name
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "user") and self.user:
            ChatConsumer.active_users.pop(str(self.user.id), None)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except Exception:
            return

        message_text = (data.get("message") or "").strip()
        to_user_id = data.get("to_user_id")

        if not message_text or not to_user_id:
            # ignore incomplete messages
            return

        from_user_id = str(self.user.id)
        from_username = self.user.username

        # Save to DB (async)
        await self.save_message(from_user_id, to_user_id, message_text)

        # Send message to recipient if online
        recipient_channel = ChatConsumer.active_users.get(str(to_user_id))
        event = {
            "type": "chat.message",
            "from_user_id": from_user_id,
            "from_username": from_username,
            "to_user_id": str(to_user_id),
            "message": message_text,
        }

        if recipient_channel:
            # send to recipient's channel
            await self.channel_layer.send(recipient_channel, event)

        # echo back to sender immediately so sender sees outgoing msg
        await self.send(text_data=json.dumps(event))

    async def chat_message(self, event):
        # Called when channel_layer.send delivers a message to this consumer
        await self.send(text_data=json.dumps({
            "from_user_id": event["from_user_id"],
            "from_username": event.get("from_username"),
            "to_user_id": event["to_user_id"],
            "message": event["message"],
        }))

    @staticmethod
    @sync_to_async
    def get_user(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    @sync_to_async
    def save_message(sender_id, receiver_id, content):
        # make sure to use the correct types/lookup for your User model PKs
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        Message.objects.create(sender=sender, receiver=receiver, content=content)
