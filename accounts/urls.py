from django.urls import path
from allauth.socialaccount.providers.google import views as google_views
from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "api/auth/google/initiate/",
        views.google_login_view,
        name="google_login_initiate",
    ),  # GET
    path(
        "api/auth/google/callback/",
        google_views.oauth2_callback,
        name="google_callback",
    ),  # POST
    path(
        "api/auth/google/callback/success/",
        views.google_callback_success,
        name="google_callback_success",
    ),  # GET
    path("api/auth/signup/", views.signup_view, name="signup"), # POST
    path("api/auth/login/", views.login_view, name="login"),    # POST
    path("api/auth/logout/", views.logout_view, name="logout"), # POST
    path("api/auth/user/", views.get_user_view, name="get_user"),    # GET
]