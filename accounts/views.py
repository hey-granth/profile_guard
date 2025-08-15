import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required


User = get_user_model()


@csrf_exempt
@require_POST
def register_view(request):
    data = json.loads(request.body)
    email: str = data.get("email")
    password: str = data.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    if not password_validation(password):
        return JsonResponse({"error": "Password must be at least 8 characters long and contain both letters and numbers"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)

    user = User.objects.create_user(email=email, password=password)
    user.save()
    return JsonResponse({"message": "User registered successfully"}, status=201)


@csrf_exempt
@require_POST
def login_view(request):
    data = json.loads(request.body)
    email: str = data.get("email")
    password: str = data.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    user = User.objects.filter(email=email).first()
    if user and user.check_password(password):
        login(request, user)
        return JsonResponse({"message": "Login successful"})
    return JsonResponse({"error": "Invalid email or password"}, status=400)



@login_required
@csrf_exempt
@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logout successful"})


def password_validation(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True