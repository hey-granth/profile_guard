import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .services import MatchingService
from core.constants import SWIPE_LIKE, SWIPE_DISLIKE

User = get_user_model()


@login_required
@csrf_exempt
@require_POST
def swipe_view(request):
    """Handle user swipe action"""
    try:
        data = json.loads(request.body)
        swiped_user_id = data.get("user_id")
        action = data.get("action")

        if not swiped_user_id or action not in [SWIPE_LIKE, SWIPE_DISLIKE]:
            return JsonResponse({"error": "Invalid swipe data"}, status=400)

        try:
            swiped_user = User.objects.get(id=swiped_user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        if swiped_user == request.user:
            return JsonResponse({"error": "Cannot swipe on yourself"}, status=400)

        # Create swipe and check for match
        match = MatchingService.create_swipe(request.user, swiped_user, action)

        response_data = {"success": True, "action": action, "match": bool(match)}

        if match:
            response_data["match_id"] = match.id
            response_data["matched_user"] = {
                "id": swiped_user.id,
                "username": swiped_user.username,
                "first_name": swiped_user.first_name,
            }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def potential_matches_view(request):
    """Get potential matches for the user"""
    try:
        limit = int(request.GET.get("limit", 10))
        potential_matches = MatchingService.get_potential_matches(request.user, limit)

        matches_data = []
        for user in potential_matches:
            user_data = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "age": getattr(user.profile, "age", None)
                if hasattr(user, "profile")
                else None,
            }

            # Add profile photos if available
            if hasattr(user, "profile") and user.profile:
                photos = user.profile.photos.all()[:3]  # Get first 3 photos
                user_data["photos"] = [
                    {
                        "id": photo.id,
                        "image_url": photo.image.url if photo.image else None,
                    }
                    for photo in photos
                ]

            matches_data.append(user_data)

        return JsonResponse(
            {"potential_matches": matches_data, "count": len(matches_data)}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def matches_view(request):
    """Get user's matches"""
    try:
        matches = MatchingService.get_user_matches(request.user)

        matches_data = []
        for match in matches:
            other_user = match.get_other_user(request.user)
            match_data = {
                "id": match.id,
                "matched_at": match.matched_at.isoformat(),
                "user": {
                    "id": other_user.id,
                    "username": other_user.username,
                    "first_name": other_user.first_name,
                },
            }

            # Add profile photo if available
            if hasattr(other_user, "profile") and other_user.profile:
                first_photo = other_user.profile.photos.first()
                if first_photo and first_photo.image:
                    match_data["user"]["profile_photo"] = first_photo.image.url

            matches_data.append(match_data)

        return JsonResponse({"matches": matches_data, "count": len(matches_data)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def liked_users_view(request):
    """Get users that the current user has liked (for chatroom)"""
    try:
        liked_users = MatchingService.get_liked_users(request.user)

        users_data = []
        for user in liked_users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
            }

            # Add profile photo if available
            if hasattr(user, "profile") and user.profile:
                first_photo = user.profile.photos.first()
                if first_photo and first_photo.image:
                    user_data["profile_photo"] = first_photo.image.url

            users_data.append(user_data)

        return JsonResponse({"liked_users": users_data, "count": len(users_data)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
