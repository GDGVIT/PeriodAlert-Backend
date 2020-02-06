from django.urls import path, include
from .views import (
    UserSignupView,
    UserLoginView,
    USerLogoutView,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("login/", UserLoginView.as_view()),
    path("signup/", UserSignupView.as_view()),
    path("logout/", USerLogoutView.as_view()),
]