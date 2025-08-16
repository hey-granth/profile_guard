from django.db import models
from django.conf import settings
from core.models import BaseModel
from core.constants import SWIPE_CHOICES, MATCH_STATUS_CHOICES, MATCH_ACTIVE


class Swipe(BaseModel):
    """Model to track user swipes"""

    swiper = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="swipes_made"
    )
    swiped = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="swipes_received",
    )
    action = models.CharField(max_length=10, choices=SWIPE_CHOICES)

    class Meta:
        unique_together = ("swiper", "swiped")
        indexes = [
            models.Index(fields=["swiper", "action"]),
            models.Index(fields=["swiped", "action"]),
        ]

    def __str__(self):
        return f"{self.swiper.username} {self.action}d {self.swiped.username}"


class Match(BaseModel):
    """Model to track matches between users"""

    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_user1",
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_user2",
    )
    status = models.CharField(
        max_length=20, choices=MATCH_STATUS_CHOICES, default=MATCH_ACTIVE
    )
    matched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2")
        indexes = [
            models.Index(fields=["user1", "status"]),
            models.Index(fields=["user2", "status"]),
        ]

    def __str__(self):
        return f"Match: {self.user1.username} & {self.user2.username}"

    def get_other_user(self, user):
        """Get the other user in the match"""
        return self.user2 if self.user1 == user else self.user1
