from django.urls import path
from . import views

app_name = "moderation"

urlpatterns = [
    path("report/", views.report_user_view, name="report_user"),
    path("block/", views.block_user_view, name="block_user"),
    path("unblock/", views.unblock_user_view, name="unblock_user"),
    path("blocked/", views.blocked_users_view, name="blocked_users"),
]
