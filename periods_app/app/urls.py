from django.urls import path, include
from .views import (
    UserSignupView,
    UserLoginView,
    UserLogoutView,
    FCMRegisterDeviceView,
    FCMPushNotificationView,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("login/", UserLoginView.as_view()),
    path("signup/", UserSignupView.as_view()),
    path("logout/", UserLogoutView.as_view()),
    path("device_register/", FCMRegisterDeviceView.as_view()),
    path("push_notification/", FCMPushNotificationView.as_view()),
]