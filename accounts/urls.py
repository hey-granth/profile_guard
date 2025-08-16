from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("clerk-webhook/", views.clerk_webhook_view, name="clerk_webhook"),
    path(
        "login-verification/", views.login_verification_view, name="login_verification"
    ),
    path("profile/", views.user_profile_view, name="user_profile"),
    path("logout/", views.logout_view, name="logout"),
]
