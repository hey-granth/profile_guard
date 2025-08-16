from django.db import models
from django.conf import settings
from pgvector.django import VectorField
from core.models import BaseModel, EmbeddingMixin
from core.constants import MAX_PROFILE_PHOTOS


class Profile(BaseModel):
    """User profile model"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    height = models.IntegerField(null=True, blank=True, help_text="Height in cm")

    # Interests and preferences
    interests = models.TextField(blank=True, help_text="Comma-separated interests")
    looking_for = models.CharField(max_length=200, blank=True)

    # Profile visibility
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def photo_count(self):
        return self.photos.count()

    @property
    def can_add_photos(self):
        return self.photo_count < MAX_PROFILE_PHOTOS


class ProfilePhoto(BaseModel, EmbeddingMixin):
    """Profile photo model with embedding for verification"""

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to="profile_photos/")
    order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["profile", "order"]),
        ]

    def __str__(self):
        return f"Photo {self.order} for {self.profile.user.username}"

    def save(self, *args, **kwargs):
        # Set as primary if it's the first photo
        if not self.pk and not self.profile.photos.exists():
            self.is_primary = True
            self.order = 1
        elif not self.order:
            # Set order as next available
            max_order = (
                self.profile.photos.aggregate(models.Max("order"))["order__max"] or 0
            )
            self.order = max_order + 1

        super().save(*args, **kwargs)


class PromptQuestion(BaseModel):
    """Predefined prompt questions for profiles"""

    question = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return self.question


class PromptAnswer(BaseModel):
    """User answers to prompt questions"""

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="prompt_answers"
    )
    question = models.ForeignKey(PromptQuestion, on_delete=models.CASCADE)
    answer = models.TextField(max_length=300)

    class Meta:
        unique_together = ("profile", "question")

    def __str__(self):
        return f"{self.profile.user.username}: {self.question.question[:50]}..."
