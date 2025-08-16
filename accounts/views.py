import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import LoginVerification
from .services import ClerkService, VerificationService
from core.utils import base64_to_embedding

User = get_user_model()


@csrf_exempt
@require_POST
def clerk_webhook_view(request):
    """Handle Clerk webhooks for user creation/updates"""
    try:
        data = json.loads(request.body)
        event_type = data.get("type")

        if event_type == "user.created":
            user_data = data.get("data")
            ClerkService.create_or_update_user(user_data)

        elif event_type == "user.updated":
            user_data = data.get("data")
            ClerkService.create_or_update_user(user_data)

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def login_verification_view(request):
    """Handle login verification with 3 images"""
    try:
        data = json.loads(request.body)
        images = data.get("images", [])  # Base64 encoded images

        if len(images) != 3:
            return JsonResponse({"error": "Exactly 3 images required"}, status=400)

        # Generate embeddings for all images
        embeddings = []
        for img_data in images:
            embedding = base64_to_embedding(img_data)
            if not embedding:
                return JsonResponse({"error": "Failed to process images"}, status=400)
            embeddings.append(embedding)

        # Create login verification record
        verification = LoginVerification.objects.create(
            user=request.user,
            embedding_1=embeddings[0],
            embedding_2=embeddings[1],
            embedding_3=embeddings[2],
            is_verified=True,
        )

        # Update user's login embeddings
        request.user.login_embeddings = embeddings
        request.user.is_verified = True
        request.user.verification_completed_at = timezone.now()
        request.user.save()

        return JsonResponse(
            {
                "success": True,
                "verification_id": verification.id,
                "message": "Login verification completed",
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def user_profile_view(request):
    """Get current user profile"""
    try:
        user = request.user
        profile_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "gender": user.gender,
            "age": user.age,
            "is_verified": user.is_verified,
            "verification_completed_at": user.verification_completed_at.isoformat()
            if user.verification_completed_at
            else None,
        }

        return JsonResponse({"user": profile_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logout successful"})
