import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .services import ProfileService
from .models import Profile, PromptQuestion

User = get_user_model()


@login_required
@require_GET
def profile_view(request):
    """Get user's profile"""
    try:
        profile = ProfileService.get_or_create_profile(request.user)

        # Get profile photos
        photos = profile.photos.all()
        photos_data = [
            {
                "id": photo.id,
                "image_url": photo.image.url if photo.image else None,
                "order": photo.order,
                "is_primary": photo.is_primary,
                "is_verified": photo.is_verified,
            }
            for photo in photos
        ]

        # Get prompt answers
        answers = profile.prompt_answers.select_related("question").all()
        answers_data = [
            {
                "question": answer.question.question,
                "answer": answer.answer,
                "question_id": answer.question.id,
            }
            for answer in answers
        ]

        profile_data = {
            "id": profile.id,
            "bio": profile.bio,
            "location": profile.location,
            "occupation": profile.occupation,
            "education": profile.education,
            "height": profile.height,
            "interests": profile.interests,
            "looking_for": profile.looking_for,
            "is_active": profile.is_active,
            "is_verified": profile.is_verified,
            "photos": photos_data,
            "prompt_answers": answers_data,
            "photo_count": profile.photo_count,
            "can_add_photos": profile.can_add_photos,
        }

        return JsonResponse({"profile": profile_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def update_profile_view(request):
    """Update user profile"""
    try:
        data = json.loads(request.body)
        profile = ProfileService.get_or_create_profile(request.user)

        # Update profile fields
        profile.bio = data.get("bio", profile.bio)
        profile.location = data.get("location", profile.location)
        profile.occupation = data.get("occupation", profile.occupation)
        profile.education = data.get("education", profile.education)
        profile.height = data.get("height", profile.height)
        profile.interests = data.get("interests", profile.interests)
        profile.looking_for = data.get("looking_for", profile.looking_for)

        profile.save()

        return JsonResponse(
            {"success": True, "message": "Profile updated successfully"}
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def upload_photos_view(request):
    """Upload profile photos with verification"""
    try:
        profile = ProfileService.get_or_create_profile(request.user)

        # Get uploaded files
        uploaded_files = request.FILES.getlist("photos")

        if not uploaded_files:
            return JsonResponse({"error": "No photos uploaded"}, status=400)

        # Update profile photos
        photos = ProfileService.update_profile_photos(profile, uploaded_files)

        photos_data = [
            {
                "id": photo.id,
                "image_url": photo.image.url,
                "order": photo.order,
                "is_primary": photo.is_primary,
                "is_verified": photo.is_verified,
            }
            for photo in photos
        ]

        return JsonResponse(
            {
                "success": True,
                "photos": photos_data,
                "message": f"{len(photos)} photos uploaded successfully",
            }
        )

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def save_prompt_answers_view(request):
    """Save prompt answers"""
    try:
        data = json.loads(request.body)
        answers_data = data.get("answers", [])

        if not answers_data:
            return JsonResponse({"error": "No answers provided"}, status=400)

        profile = ProfileService.get_or_create_profile(request.user)
        answers = ProfileService.save_prompt_answers(profile, answers_data)

        return JsonResponse(
            {
                "success": True,
                "answers_saved": len(answers),
                "message": "Prompt answers saved successfully",
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_GET
def prompt_questions_view(request):
    """Get all active prompt questions"""
    try:
        questions = ProfileService.get_active_prompt_questions()

        questions_data = [
            {
                "id": q.id,
                "question": q.question,
                "order": q.order,
            }
            for q in questions
        ]

        return JsonResponse({"questions": questions_data, "count": len(questions_data)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_GET
def user_profile_view(request, user_id):
    """Get another user's profile (for matching)"""
    try:
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
        except (User.DoesNotExist, Profile.DoesNotExist):
            return JsonResponse({"error": "Profile not found"}, status=404)

        # Get profile photos
        photos = profile.photos.filter(is_verified=True)
        photos_data = [
            {
                "id": photo.id,
                "image_url": photo.image.url,
                "order": photo.order,
                "is_primary": photo.is_primary,
            }
            for photo in photos
        ]

        # Get prompt answers
        answers = profile.prompt_answers.select_related("question").all()
        answers_data = [
            {
                "question": answer.question.question,
                "answer": answer.answer,
            }
            for answer in answers
        ]

        profile_data = {
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "age": user.age,
            },
            "bio": profile.bio,
            "location": profile.location,
            "occupation": profile.occupation,
            "education": profile.education,
            "height": profile.height,
            "interests": profile.interests,
            "looking_for": profile.looking_for,
            "photos": photos_data,
            "prompt_answers": answers_data,
        }

        return JsonResponse({"profile": profile_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
