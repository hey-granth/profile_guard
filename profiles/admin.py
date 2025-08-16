from django.contrib import admin
from .models import Profile, ProfilePhoto, PromptQuestion, PromptAnswer


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_verified', 'created_at']
    search_fields = ['user__email', 'user__username']


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ['profile', 'order', 'is_primary', 'is_verified']
    list_filter = ['is_primary', 'is_verified', 'created_at']


@admin.register(PromptQuestion)
class PromptQuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'is_active', 'order']
    list_filter = ['is_active']


@admin.register(PromptAnswer)
class PromptAnswerAdmin(admin.ModelAdmin):
    list_display = ['profile', 'question', 'created_at']
    list_filter = ['created_at']
