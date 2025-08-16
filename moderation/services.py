"""Moderation services"""

from typing import List, Optional
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Report, BlockedUser, BanRecord

User = get_user_model()


class ModerationService:
    """Service for moderation actions"""

    @staticmethod
    def create_report(
        reporter: User, reported_user: User, reason: str, description: str = ""
    ) -> Report:
        """Create a report"""
        if reporter == reported_user:
            raise ValueError("Cannot report yourself")

        report, created = Report.objects.get_or_create(
            reporter=reporter,
            reported_user=reported_user,
            defaults={"reason": reason, "description": description},
        )

        if not created:
            # Update existing report
            report.reason = reason
            report.description = description
            report.save()

        return report

    @staticmethod
    def block_user(blocker: User, blocked_user: User, reason: str = "") -> BlockedUser:
        """Block a user"""
        if blocker == blocked_user:
            raise ValueError("Cannot block yourself")

        blocked, created = BlockedUser.objects.get_or_create(
            blocker=blocker, blocked=blocked_user, defaults={"reason": reason}
        )

        return blocked

    @staticmethod
    def unblock_user(blocker: User, blocked_user: User) -> bool:
        """Unblock a user"""
        try:
            blocked = BlockedUser.objects.get(blocker=blocker, blocked=blocked_user)
            blocked.delete()
            return True
        except BlockedUser.DoesNotExist:
            return False

    @staticmethod
    def is_blocked(user1: User, user2: User) -> bool:
        """Check if user1 has blocked user2 or vice versa"""
        from django.db import models

        return BlockedUser.objects.filter(
            models.Q(blocker=user1, blocked=user2)
            | models.Q(blocker=user2, blocked=user1)
        ).exists()

    @staticmethod
    def get_blocked_users(user: User) -> List[User]:
        """Get users blocked by the given user"""
        blocked_ids = BlockedUser.objects.filter(blocker=user).values_list(
            "blocked_id", flat=True
        )

        return User.objects.filter(id__in=blocked_ids)

    @staticmethod
    def ban_user(
        user: User, banned_by: User, reason: str, expires_at=None
    ) -> BanRecord:
        """Ban a user"""
        with transaction.atomic():
            # Deactivate existing bans
            BanRecord.objects.filter(user=user, is_active=True).update(is_active=False)

            # Create new ban
            ban = BanRecord.objects.create(
                user=user,
                banned_by=banned_by,
                reason=reason,
                expires_at=expires_at,
                is_active=True,
            )

            # Deactivate user account
            user.is_active = False
            user.save()

            return ban

    @staticmethod
    def unban_user(user: User) -> bool:
        """Unban a user"""
        with transaction.atomic():
            # Deactivate all bans
            updated = BanRecord.objects.filter(user=user, is_active=True).update(
                is_active=False
            )

            if updated:
                # Reactivate user account
                user.is_active = True
                user.save()
                return True

            return False

    @staticmethod
    def is_banned(user: User) -> bool:
        """Check if user is currently banned"""
        from django.db import models

        active_ban = (
            BanRecord.objects.filter(user=user, is_active=True)
            .filter(
                models.Q(expires_at__isnull=True)
                | models.Q(expires_at__gt=timezone.now())
            )
            .exists()
        )

        return active_ban

    @staticmethod
    def get_pending_reports() -> List[Report]:
        """Get all pending reports"""
        return (
            Report.objects.filter(is_resolved=False)
            .select_related("reporter", "reported_user")
            .order_by("-created_at")
        )
