from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, EmailOTP, UserToken


# -------------------------
#   USER SERIALIZER
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uid", "email", "full_name", "phone", "avatar", "is_active", "date_joined"]


# -------------------------
#   REGISTER SERIALIZER
# -------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "full_name", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data.get("full_name", "")
        )
        return user


# -------------------------
#    OTP VERIFY SERIALIZER
# -------------------------
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


# -------------------------
#     LOGIN SERIALIZER
# -------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("Account is not verified")

        attrs["user"] = user
        return attrs


# -------------------------
#      TOKEN SERIALIZER
# -------------------------
class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = ["access_token", "refresh_token"]


from address.models import Address


class UserSummarySerializer(serializers.Serializer):
    uid = serializers.UUIDField()
    full_name = serializers.CharField()
    email = serializers.EmailField()




# -------------------------
#   FORGOT PASSWORD
# -------------------------

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)
