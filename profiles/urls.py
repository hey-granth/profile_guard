from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("", views.profile_view, name="profile"),
    path("update/", views.update_profile_view, name="update_profile"),
    path("upload-photos/", views.upload_photos_view, name="upload_photos"),
    path("prompt-answers/", views.save_prompt_answers_view, name="save_prompt_answers"),
    path("questions/", views.prompt_questions_view, name="prompt_questions"),
    path("<int:user_id>/", views.user_profile_view, name="user_profile"),
]
