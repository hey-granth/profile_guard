import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .services import ChatService
from .models import ChatRoom, Message
from matching.models import Match

User = get_user_model()


@login_required
@csrf_exempt
@require_POST
def send_message_view(request):
    """Send a message in a chat room"""
    try:
        data = json.loads(request.body)
        chat_room_id = data.get("chat_room_id")
        content = data.get("content", "").strip()

        if not chat_room_id or not content:
            return JsonResponse(
                {"error": "Chat room ID and content required"}, status=400
            )

        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            return JsonResponse({"error": "Chat room not found"}, status=404)

        message = ChatService.send_message(request.user, chat_room, content)

        if not message:
            return JsonResponse({"error": "Cannot send message"}, status=403)

        return JsonResponse(
            {
                "success": True,
                "message": {
                    "id": message.id,
                    "content": message.content,
                    "sender": message.sender.username,
                    "created_at": message.created_at.isoformat(),
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def chat_rooms_view(request):
    """Get user's chat rooms"""
    try:
        chat_rooms = ChatService.get_user_chat_rooms(request.user)

        rooms_data = []
        for room in chat_rooms:
            # Get other participants
            other_participants = room.participants.exclude(id=request.user.id)

            # Get last message
            last_message = room.messages.first()

            room_data = {
                "id": room.id,
                "chat_type": room.chat_type,
                "name": room.name,
                "participants": [
                    {
                        "id": p.id,
                        "username": p.username,
                        "first_name": p.first_name,
                    }
                    for p in other_participants
                ],
                "last_message": {
                    "content": last_message.content,
                    "sender": last_message.sender.username,
                    "created_at": last_message.created_at.isoformat(),
                }
                if last_message
                else None,
                "updated_at": room.updated_at.isoformat(),
            }

            rooms_data.append(room_data)

        return JsonResponse({"chat_rooms": rooms_data, "count": len(rooms_data)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def chat_messages_view(request, chat_room_id):
    """Get messages for a chat room"""
    try:
        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            return JsonResponse({"error": "Chat room not found"}, status=404)

        # Check if user is participant
        if not chat_room.participants.filter(id=request.user.id).exists():
            return JsonResponse({"error": "Access denied"}, status=403)

        limit = int(request.GET.get("limit", 50))
        messages = ChatService.get_chat_messages(chat_room, limit)

        # Mark messages as read
        ChatService.mark_messages_as_read(request.user, chat_room)

        messages_data = [
            {
                "id": msg.id,
                "content": msg.content,
                "sender": {
                    "id": msg.sender.id,
                    "username": msg.sender.username,
                    "first_name": msg.sender.first_name,
                },
                "created_at": msg.created_at.isoformat(),
                "is_own": msg.sender == request.user,
            }
            for msg in messages
        ]

        return JsonResponse({"messages": messages_data, "count": len(messages_data)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def create_private_chat_view(request):
    """Create private chat from match"""
    try:
        data = json.loads(request.body)
        match_id = data.get("match_id")

        if not match_id:
            return JsonResponse({"error": "Match ID required"}, status=400)

        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return JsonResponse({"error": "Match not found"}, status=404)

        # Check if user is part of the match
        if request.user not in [match.user1, match.user2]:
            return JsonResponse({"error": "Access denied"}, status=403)

        chat_room = ChatService.get_or_create_private_chat(match)

        return JsonResponse(
            {
                "success": True,
                "chat_room": {
                    "id": chat_room.id,
                    "chat_type": chat_room.chat_type,
                    "created_at": chat_room.created_at.isoformat(),
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
