from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("send/", views.send_message_view, name="send_message"),
    path("rooms/", views.chat_rooms_view, name="chat_rooms"),
    path(
        "rooms/<int:chat_room_id>/messages/",
        views.chat_messages_view,
        name="chat_messages",
    ),
    path("create-private/", views.create_private_chat_view, name="create_private_chat"),
]
