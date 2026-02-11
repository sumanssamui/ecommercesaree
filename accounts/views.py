from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer
from rest_framework.permissions import AllowAny

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
# USER REGISTER API
# -----------------------------
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Save refresh token in DB (optional but recommended)
        UserToken.objects.update_or_create(
            user=user,
            defaults={
                "refresh_token": refresh_token
            }
        )

        response = Response({
            "message": "Login Successful",
            "user": UserSerializer(user).data,
            "access": access_token
        }, status=200)

        # ✅ STORE REFRESH TOKEN IN HTTP-ONLY COOKIE
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,      # True in production (HTTPS)
            samesite="Strict",
            max_age=7 * 24 * 60 * 60  # 7 days
        )

        return response



from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class RefreshAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "No refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)

            return Response(
                {"access": access},
                status=status.HTTP_200_OK
            )

        except TokenError:
            response = Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

            # ❌ Remove bad cookie
            response.delete_cookie("refresh_token")

            return response




class LogoutAPIView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"})
        response.delete_cookie("refresh_token")
        UserToken.objects.filter(user=request.user).delete()
        return response






from rest_framework.permissions import IsAuthenticated
from cart.models import CartItem
from wishlist.models import WishlistItem
from address.models import Address
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSummarySerializer


class UserSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Cart count
        cart_count = CartItem.objects.filter(cart__user=user).count()

        # Wishlist count
        wishlist_count = WishlistItem.objects.filter(wishlist__user=user).count()

        # Default address (light fields only)
        default_address = Address.objects.filter(
            user=user, is_default=True
        ).values(
            "id",
            "city",
            "state",
            "pincode"
        ).first()

        return Response({
            "user": UserSummarySerializer(user).data,
            "cart_count": cart_count,
            "wishlist_count": wishlist_count,
            "default_address": default_address
        })





# -----------------------------
# FORGOT PASSWORD (SEND OTP)
# -----------------------------
class ForgotPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        otp = create_otp(user)
        send_otp_email(email, otp)

        return Response({
            "message": "Password reset OTP sent"
        }, status=200)


# -----------------------------
# RESET PASSWORD
# -----------------------------
class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
            otp_entry = user.email_otps.filter(
                otp=otp,
                is_used=False
            ).latest("created_at")
        except Exception:
            return Response({"error": "Invalid or expired OTP"}, status=400)

        user.set_password(new_password)
        user.save()

        otp_entry.is_used = True
        otp_entry.save()

        return Response({
            "message": "Password reset successful"
        }, status=200)
