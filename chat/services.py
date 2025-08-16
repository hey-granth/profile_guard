"""Chat service layer"""

from typing import Optional, List
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from matching.models import Match
from core.constants import CHAT_PRIVATE, CHAT_ROOM

User = get_user_model()


class ChatService:
    """Service class for handling chat logic"""

    @staticmethod
    def get_or_create_private_chat(match: Match) -> ChatRoom:
        """Get or create private chat room for a match"""
        chat_room, created = ChatRoom.objects.get_or_create(
            match=match, defaults={"chat_type": CHAT_PRIVATE, "is_active": True}
        )

        if created:
            # Add participants
            chat_room.participants.add(match.user1, match.user2)

        return chat_room

    @staticmethod
    def can_send_message(user: User, chat_room: ChatRoom) -> bool:
        """Check if user can send message in chat room"""
        # User must be participant
        if not chat_room.participants.filter(id=user.id).exists():
            return False

        # For private chats, only females can initiate messaging
        if chat_room.chat_type == CHAT_PRIVATE and chat_room.match:
            # Check if this is the first message
            if not chat_room.messages.exists():
                return user.gender == "F"

        return True

    @staticmethod
    def send_message(
        user: User, chat_room: ChatRoom, content: str
    ) -> Optional[Message]:
        """Send a message in chat room"""
        if not ChatService.can_send_message(user, chat_room):
            return None

        with transaction.atomic():
            message = Message.objects.create(
                chat_room=chat_room, sender=user, content=content
            )

            # Update chat room timestamp
            chat_room.save(update_fields=["updated_at"])

            return message

    @staticmethod
    def get_user_chat_rooms(user: User) -> List[ChatRoom]:
        """Get all chat rooms for a user"""
        return (
            ChatRoom.objects.filter(participants=user, is_active=True)
            .prefetch_related("participants", "messages")
            .order_by("-updated_at")
        )

    @staticmethod
    def get_chat_messages(chat_room: ChatRoom, limit: int = 50) -> List[Message]:
        """Get messages for a chat room"""
        return chat_room.messages.select_related("sender").order_by("created_at")[
            :limit
        ]

    @staticmethod
    def mark_messages_as_read(user: User, chat_room: ChatRoom):
        """Mark all messages in chat room as read for user"""
        Message.objects.filter(chat_room=chat_room, is_read=False).exclude(
            sender=user
        ).update(is_read=True)
