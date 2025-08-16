from django.urls import path
from . import views

app_name = "matching"

urlpatterns = [
    path("swipe/", views.swipe_view, name="swipe"),
    path("potential/", views.potential_matches_view, name="potential_matches"),
    path("matches/", views.matches_view, name="matches"),
    path("liked/", views.liked_users_view, name="liked_users"),
]
