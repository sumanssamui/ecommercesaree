from django.urls import path
from .views import (
    userroot,
    RegisterAPIView,
    LoginAPIView,
    VerifyOTPAPIView
)

urlpatterns = [
    path('', userroot, name='userroot'),

    # Auth Routes
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify_otp'),
]
