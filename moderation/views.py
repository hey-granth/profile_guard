import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .services import ModerationService
from core.constants import REPORT_REASONS

User = get_user_model()


@login_required
@csrf_exempt
@require_POST
def report_user_view(request):
    """Report a user"""
    try:
        data = json.loads(request.body)
        reported_user_id = data.get("user_id")
        reason = data.get("reason")
        description = data.get("description", "")

        if not reported_user_id or not reason:
            return JsonResponse({"error": "User ID and reason required"}, status=400)

        if reason not in [choice[0] for choice in REPORT_REASONS]:
            return JsonResponse({"error": "Invalid reason"}, status=400)

        try:
            reported_user = User.objects.get(id=reported_user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        report = ModerationService.create_report(
            request.user, reported_user, reason, description
        )

        return JsonResponse(
            {
                "success": True,
                "report_id": report.id,
                "message": "Report submitted successfully",
            }
        )

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def block_user_view(request):
    """Block a user"""
    try:
        data = json.loads(request.body)
        blocked_user_id = data.get("user_id")
        reason = data.get("reason", "")

        if not blocked_user_id:
            return JsonResponse({"error": "User ID required"}, status=400)

        try:
            blocked_user = User.objects.get(id=blocked_user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        ModerationService.block_user(request.user, blocked_user, reason)

        return JsonResponse({"success": True, "message": "User blocked successfully"})

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def unblock_user_view(request):
    """Unblock a user"""
    try:
        data = json.loads(request.body)
        blocked_user_id = data.get("user_id")

        if not blocked_user_id:
            return JsonResponse({"error": "User ID required"}, status=400)

        try:
            blocked_user = User.objects.get(id=blocked_user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        success = ModerationService.unblock_user(request.user, blocked_user)

        if success:
            return JsonResponse(
                {"success": True, "message": "User unblocked successfully"}
            )
        else:
            return JsonResponse({"error": "User was not blocked"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def blocked_users_view(request):
    """Get blocked users"""
    try:
        blocked_users = ModerationService.get_blocked_users(request.user)

        users_data = [
            {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
            }
            for user in blocked_users
        ]

        return JsonResponse({"blocked_users": users_data, "count": len(users_data)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
