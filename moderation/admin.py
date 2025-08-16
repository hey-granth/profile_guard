from django.contrib import admin
from .models import Report, BlockedUser, BanRecord


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reported_user', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved', 'created_at']
    search_fields = ['reporter__email', 'reported_user__email']


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']
    list_filter = ['created_at']
    search_fields = ['blocker__email', 'blocked__email']


@admin.register(BanRecord)
class BanRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'banned_by', 'is_active', 'expires_at', 'created_at']
    list_filter = ['is_active', 'expires_at', 'created_at']
    search_fields = ['user__email', 'banned_by__email']
