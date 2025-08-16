"""Account services for Clerk integration and verification"""

from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import LoginVerification

User = get_user_model()


class ClerkService:
    """Service for handling Clerk integration"""

    @staticmethod
    def create_or_update_user(clerk_data: Dict[str, Any]) -> User:
        """Create or update user from Clerk webhook data"""
        clerk_id = clerk_data.get("id")
        email = clerk_data.get("email_addresses", [{}])[0].get("email_address")

        if not clerk_id or not email:
            raise ValueError("Missing required Clerk data")

        # Get or create user
        user, created = User.objects.get_or_create(
            clerk_id=clerk_id,
            defaults={
                "email": email,
                "username": email,
                "first_name": clerk_data.get("first_name", ""),
                "last_name": clerk_data.get("last_name", ""),
                "is_active": True,
            },
        )

        # Update user data if not created
        if not created:
            user.email = email
            user.username = email
            user.first_name = clerk_data.get("first_name", "")
            user.last_name = clerk_data.get("last_name", "")
            user.save()

        return user

    @staticmethod
    def get_user_by_clerk_id(clerk_id: str) -> Optional[User]:
        """Get user by Clerk ID"""
        try:
            return User.objects.get(clerk_id=clerk_id)
        except User.DoesNotExist:
            return None


class VerificationService:
    """Service for handling user verification"""

    @staticmethod
    def create_login_verification(user: User, embeddings: list) -> LoginVerification:
        """Create login verification with embeddings"""
        if len(embeddings) != 3:
            raise ValueError("Exactly 3 embeddings required")

        verification = LoginVerification.objects.create(
            user=user,
            embedding_1=embeddings[0],
            embedding_2=embeddings[1],
            embedding_3=embeddings[2],
            is_verified=True,
        )

        # Update user verification status
        user.login_embeddings = embeddings
        user.is_verified = True
        user.verification_completed_at = timezone.now()
        user.save()

        return verification

    @staticmethod
    def get_user_login_embeddings(user: User) -> Optional[list]:
        """Get user's login embeddings"""
        return user.login_embeddings if user.login_embeddings else None
