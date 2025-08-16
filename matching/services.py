"""Matching service layer"""

from typing import Optional, List
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Swipe, Match
from core.constants import SWIPE_LIKE, MATCH_ACTIVE

User = get_user_model()


class MatchingService:
    """Service class for handling matching logic"""

    @staticmethod
    def create_swipe(swiper: User, swiped: User, action: str) -> Optional[Match]:
        """
        Create a swipe and check for mutual match
        Returns Match object if mutual like, None otherwise
        """
        with transaction.atomic():
            # Create or update swipe
            swipe, created = Swipe.objects.update_or_create(
                swiper=swiper, swiped=swiped, defaults={"action": action}
            )

            # Check for mutual like
            if action == SWIPE_LIKE:
                mutual_swipe = Swipe.objects.filter(
                    swiper=swiped, swiped=swiper, action=SWIPE_LIKE
                ).first()

                if mutual_swipe:
                    # Create match (ensure consistent ordering)
                    user1, user2 = (
                        (swiper, swiped) if swiper.id < swiped.id else (swiped, swiper)
                    )
                    match, match_created = Match.objects.get_or_create(
                        user1=user1, user2=user2, defaults={"status": MATCH_ACTIVE}
                    )
                    return match

            return None

    @staticmethod
    def get_potential_matches(user: User, limit: int = 10) -> List[User]:
        """Get potential matches for a user (users they haven't swiped on)"""
        # Get users already swiped on
        swiped_user_ids = Swipe.objects.filter(swiper=user).values_list(
            "swiped_id", flat=True
        )

        # Get potential matches (exclude self and already swiped users)
        potential_matches = (
            User.objects.filter(is_active=True)
            .exclude(id__in=list(swiped_user_ids) + [user.id])
            .select_related("profile")[:limit]
        )

        return list(potential_matches)

    @staticmethod
    def get_user_matches(user: User) -> List[Match]:
        """Get all active matches for a user"""
        from django.db import models

        return (
            Match.objects.filter(
                models.Q(user1=user) | models.Q(user2=user), status=MATCH_ACTIVE
            )
            .select_related("user1", "user2")
            .order_by("-matched_at")
        )

    @staticmethod
    def get_liked_users(user: User) -> List[User]:
        """Get users that the current user has liked"""
        liked_user_ids = Swipe.objects.filter(
            swiper=user, action=SWIPE_LIKE
        ).values_list("swiped_id", flat=True)

        return User.objects.filter(id__in=liked_user_ids).select_related("profile")
