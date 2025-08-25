from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ["name", "chat_type", "is_active", "created_at"]
    list_filter = ["chat_type", "is_active", "created_at"]
    filter_horizontal = ["participants"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "chat_room", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["sender__email", "content"]
