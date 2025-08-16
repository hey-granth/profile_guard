import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from .services import ChatService

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        self.room_group_name = f"chat_{self.chat_room_id}"
        self.user = self.scope["user"]

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user can access this chat room
        can_access = await self.can_access_chat_room()
        if not can_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get("type", "message")

            if message_type == "message":
                content = text_data_json.get("content", "").strip()

                if content:
                    # Save message to database
                    message = await self.save_message(content)

                    if message:
                        # Send message to room group
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "chat_message",
                                "message": {
                                    "id": message.id,
                                    "content": message.content,
                                    "sender": {
                                        "id": message.sender.id,
                                        "username": message.sender.username,
                                        "first_name": message.sender.first_name,
                                    },
                                    "created_at": message.created_at.isoformat(),
                                },
                            },
                        )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))

    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"type": "message", "message": message}))

    @database_sync_to_async
    def can_access_chat_room(self):
        try:
            chat_room = ChatRoom.objects.get(id=self.chat_room_id)
            return chat_room.participants.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        try:
            chat_room = ChatRoom.objects.get(id=self.chat_room_id)
            return ChatService.send_message(self.user, chat_room, content)
        except ChatRoom.DoesNotExist:
            return None
