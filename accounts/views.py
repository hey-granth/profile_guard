import json
import jwt
from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.urls.base import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from config import Config
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


User = get_user_model()


def generate_jwt(user):
    payload: dict = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "exp": timezone.now() + timezone.timedelta(hours=24),  # expiration time of jwt
        "iat": timezone.now(),  # time at which jwt was issued
    }
    token: str = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return token


@csrf_exempt
@require_POST
def signup_view(request):
    """
    Signup view for user registration.
    """
    """ Example payload:
    {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
    }
    """
    try:
        data: dict = json.loads(request.body)
        username: str = data.get("username")
        email: str = data.get("email")
        password: str = data.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required"}, status=400
            )

        # email validation
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"error": "Invalid email format"}, status=400)

        # username validation
        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)

        # password validation
        if (
            (len(password) < 8)
            or (not any(char.isdigit() for char in password))
            or (not any(char.isalpha() for char in password))
            or (not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password))
        ):
            return JsonResponse(
                {
                    "error": """
            - Password must be at least 8 characters long
            - Password must contain at least one letter and one number
            - Password must contain at least one special character
            """
                },
                status=400,
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        user: User = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.save()
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
        token: str = generate_jwt(user)
        return JsonResponse(
            {"message": "User created successfully", "token": token}, status=201
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def login_view(request):
    """
    Login view for user authentication.
    """
    """ Example payload:
    {
    "email": "john@example.com",
    "password": "securepassword123"
    }
    """
    try:
        data: dict = json.loads(request.body)
        email: str = data.get("email")
        password: str = data.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required"}, status=400
            )

        user = authenticate(request, email=email, password=password)
        if user is not None:
            token: str = generate_jwt(user)
            login(request, user)
            return JsonResponse({"token": token}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_POST
def logout_view(request):
    """
    Logout view for user authentication.
    """
    """
    Example payload:
    {
    "token": "jwt_token_here"
    }
    """
    try:
        logout(request)
        # the jwt will be discarded by the client after logout
        return JsonResponse({"message": "Logout successful"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_GET
def google_login_view(request):
    """
    Google login view for user authentication.
    """
    try:
        adapter = GoogleOAuth2Adapter(request)
        provider = adapter.get_provider()

        callback_url: str = request.build_absolute_uri(reverse("accounts:google_callback"))
        login_url: str = provider.get_login_url(
            request,
            scope=["profile", "email"],
            callback_url=callback_url,
        )

        return JsonResponse({"login_url": login_url}, status=200)

    except Exception as e:
        return JsonResponse(
            {"error": f"Google Login URL could not be generated: {str(e)}"}, status=500
        )


@require_GET
def google_callback_success(request):
    """
    Callback view to authenticate Google user, generate JWT and then return to the client.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated"}, status=401)

    token: str = generate_jwt(request.user)
    return JsonResponse({"token": token, "email": request.user.email}, status=200)


@login_required
@require_GET
def get_user_view(request):
    """
    View to get the authenticated user's details.
    """
    try:
        user: User = request.user
        user_data: dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        return JsonResponse({"user": user_data}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)