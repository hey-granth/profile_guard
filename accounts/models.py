from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField
from core.models import BaseModel
from core.constants import GENDER_CHOICES


class User(AbstractUser):
    """Custom user model with Clerk integration"""

    clerk_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Login verification embeddings (3 images captured during login)
    login_embeddings = ArrayField(
        VectorField(dimensions=512), size=3, null=True, blank=True
    )

    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_completed_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def age(self):
        if self.date_of_birth:
            from datetime import date

            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None


class LoginVerification(BaseModel):
    """Model to store login verification images and embeddings"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_verifications"
    )
    image_1 = models.ImageField(upload_to="login_verification/", null=True, blank=True)
    image_2 = models.ImageField(upload_to="login_verification/", null=True, blank=True)
    image_3 = models.ImageField(upload_to="login_verification/", null=True, blank=True)
    embedding_1 = VectorField(dimensions=512, null=True, blank=True)
    embedding_2 = VectorField(dimensions=512, null=True, blank=True)
    embedding_3 = VectorField(dimensions=512, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Login verification for {self.user.email}"
