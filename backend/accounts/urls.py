from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, CurrentUserView, UserProfileUpdateView

app_name = "accounts"

urlpatterns = [
    # Auth endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # User and Profile endpoints
    path("me/", CurrentUserView.as_view(), name="current_user"),
    path("profile/", UserProfileUpdateView.as_view(), name="profile_update"),
]