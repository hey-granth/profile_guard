from django.contrib import admin
from .models import User, LoginVerification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "is_verified", "date_joined"]
    list_filter = ["is_verified", "is_active", "date_joined"]
    search_fields = ["email", "username"]


@admin.register(LoginVerification)
class LoginVerificationAdmin(admin.ModelAdmin):
    list_display = ["user", "is_verified", "created_at"]
    list_filter = ["is_verified", "created_at"]
