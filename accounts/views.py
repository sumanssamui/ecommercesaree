from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from .models import User, UserToken
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyOTPSerializer,
    UserSerializer
)
from .utils import create_otp
from .email_service import send_otp_email
from rest_framework_simplejwt.tokens import RefreshToken


# -----------------------------
# SIMPLE ROOT CHECK
# -----------------------------
def userroot(request):
    data = {
        "message": "Hello User",
        "status": "success"
    }
    return JsonResponse(data)



# -----------------------------
# USER REGISTER API
# -----------------------------
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=400)

        user = serializer.save()

        # Generate OTP
        otp = create_otp(user)
        send_otp_email(email, otp)

        return Response({
            "message": "OTP sent to email",
            "email": email
        }, status=201)



# -----------------------------
# VERIFY OTP API
# -----------------------------
class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
            otp_entry = user.email_otps.filter(otp=otp, is_used=False).latest("created_at")
        except Exception:
            return Response({"error": "Invalid or expired OTP"}, status=400)

        # Activate user
        user.is_active = True
        user.save()

        otp_entry.is_used = True
        otp_entry.save()

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)

        UserToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }
        )

        return Response({
            "message": "OTP Verified",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=200)



# -----------------------------
# LOGIN API
# -----------------------------
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        UserToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }
        )

        return Response({
            "message": "Login Successful",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=200)
