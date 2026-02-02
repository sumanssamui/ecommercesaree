from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    VerifyOTPAPIView,
    UserSummaryAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView
)

urlpatterns = [

    # Auth Routes
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify_otp'),
    path('summary/', UserSummaryAPIView.as_view(), name='user_summary'),

       # Password reset
    path('forgot-password/', ForgotPasswordAPIView.as_view()),
    path('reset-password/', ResetPasswordAPIView.as_view()),

]
