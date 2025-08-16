"""Profile services for image verification and management"""

from typing import List, Optional
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Profile, ProfilePhoto, PromptAnswer, PromptQuestion
from core.utils import validate_image_similarity, process_uploaded_image
from core.constants import MAX_PROFILE_PHOTOS
from accounts.services import VerificationService

User = get_user_model()


class ProfileService:
    """Service for profile management"""

    @staticmethod
    def get_or_create_profile(user: User) -> Profile:
        """Get or create profile for user"""
        profile, created = Profile.objects.get_or_create(
            user=user, defaults={"is_active": True}
        )
        return profile

    @staticmethod
    def add_profile_photo(
        profile: Profile, image_file, order: int = None
    ) -> Optional[ProfilePhoto]:
        """Add profile photo with verification"""
        if not profile.can_add_photos:
            raise ValueError(f"Maximum {MAX_PROFILE_PHOTOS} photos allowed")

        # Generate embedding for the new image
        embedding = process_uploaded_image(image_file)
        if not embedding:
            raise ValueError("Failed to process image")

        # Get user's login embeddings for verification
        login_embeddings = VerificationService.get_user_login_embeddings(profile.user)
        if not login_embeddings:
            raise ValueError("User must complete login verification first")

        # Verify image similarity
        is_verified = validate_image_similarity([embedding], login_embeddings)

        with transaction.atomic():
            photo = ProfilePhoto.objects.create(
                profile=profile,
                image=image_file,
                embedding=embedding,
                is_verified=is_verified,
                order=order,
            )

            return photo

    @staticmethod
    def update_profile_photos(
        profile: Profile, image_files: List
    ) -> List[ProfilePhoto]:
        """Update multiple profile photos with verification"""
        if len(image_files) > MAX_PROFILE_PHOTOS:
            raise ValueError(f"Maximum {MAX_PROFILE_PHOTOS} photos allowed")

        # Generate embeddings for all new images
        new_embeddings = []
        for image_file in image_files:
            embedding = process_uploaded_image(image_file)
            if not embedding:
                raise ValueError("Failed to process one or more images")
            new_embeddings.append(embedding)

        # Get user's login embeddings for verification
        login_embeddings = VerificationService.get_user_login_embeddings(profile.user)
        if not login_embeddings:
            raise ValueError("User must complete login verification first")

        # Verify all images
        is_verified = validate_image_similarity(new_embeddings, login_embeddings)
        if not is_verified:
            raise ValueError("Images do not match login verification photos")

        with transaction.atomic():
            # Delete existing photos
            profile.photos.all().delete()

            # Create new photos
            photos = []
            for i, (image_file, embedding) in enumerate(
                zip(image_files, new_embeddings)
            ):
                photo = ProfilePhoto.objects.create(
                    profile=profile,
                    image=image_file,
                    embedding=embedding,
                    is_verified=True,
                    order=i + 1,
                    is_primary=(i == 0),
                )
                photos.append(photo)

            return photos

    @staticmethod
    def save_prompt_answers(
        profile: Profile, answers_data: List[dict]
    ) -> List[PromptAnswer]:
        """Save prompt answers for profile"""
        answers = []

        with transaction.atomic():
            for answer_data in answers_data:
                question_id = answer_data.get("question_id")
                answer_text = answer_data.get("answer", "").strip()

                if not question_id or not answer_text:
                    continue

                try:
                    question = PromptQuestion.objects.get(
                        id=question_id, is_active=True
                    )
                    answer, created = PromptAnswer.objects.update_or_create(
                        profile=profile,
                        question=question,
                        defaults={"answer": answer_text},
                    )
                    answers.append(answer)
                except PromptQuestion.DoesNotExist:
                    continue

        return answers

    @staticmethod
    def get_active_prompt_questions() -> List[PromptQuestion]:
        """Get all active prompt questions"""
        return list(PromptQuestion.objects.filter(is_active=True).order_by("order"))
