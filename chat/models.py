from django.db import models
from django.conf import settings
from core.models import BaseModel
from core.constants import CHAT_TYPE_CHOICES, CHAT_PRIVATE


class ChatRoom(BaseModel):
    """Model for chat rooms (private chats and group chats)"""

    name = models.CharField(max_length=255, blank=True)
    chat_type = models.CharField(
        max_length=10, choices=CHAT_TYPE_CHOICES, default=CHAT_PRIVATE
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="chat_rooms"
    )
    match = models.OneToOneField(
        "matching.Match",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_room",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["chat_type", "is_active"]),
        ]

    def __str__(self):
        if self.name:
            return self.name
        participants = list(self.participants.all()[:2])
        if len(participants) == 2:
            return f"Chat: {participants[0].username} & {participants[1].username}"
        return f"Chat Room {self.id}"


class Message(BaseModel):
    """Model for chat messages"""

    chat_room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["chat_room", "-created_at"]),
            models.Index(fields=["sender", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."
