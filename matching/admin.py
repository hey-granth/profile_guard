from django.contrib import admin
from .models import Swipe, Match


@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):
    list_display = ["swiper", "swiped", "action", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["swiper__email", "swiped__email"]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ["user1", "user2", "status", "matched_at"]
    list_filter = ["status", "matched_at"]
    search_fields = ["user1__email", "user2__email"]
