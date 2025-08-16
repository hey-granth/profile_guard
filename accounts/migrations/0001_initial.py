# Generated migration for accounts app

from django.db import migrations, models
import django.contrib.auth.models
import django.utils.timezone
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "clerk_id",
                    models.CharField(
                        blank=True, max_length=255, null=True, unique=True
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone_number", models.CharField(blank=True, max_length=20)),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("M", "Male"),
                            ("F", "Female"),
                            ("NB", "Non-binary"),
                            ("O", "Other"),
                        ],
                        max_length=2,
                    ),
                ),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "login_embeddings",
                    ArrayField(
                        VectorField(dimensions=512), blank=True, null=True, size=3
                    ),
                ),
                ("is_verified", models.BooleanField(default=False)),
                (
                    "verification_completed_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="LoginVerification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "image_1",
                    models.ImageField(
                        blank=True, null=True, upload_to="login_verification/"
                    ),
                ),
                (
                    "image_2",
                    models.ImageField(
                        blank=True, null=True, upload_to="login_verification/"
                    ),
                ),
                (
                    "image_3",
                    models.ImageField(
                        blank=True, null=True, upload_to="login_verification/"
                    ),
                ),
                ("embedding_1", VectorField(blank=True, dimensions=512, null=True)),
                ("embedding_2", VectorField(blank=True, dimensions=512, null=True)),
                ("embedding_3", VectorField(blank=True, dimensions=512, null=True)),
                ("is_verified", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="login_verifications",
                        to="accounts.user",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
