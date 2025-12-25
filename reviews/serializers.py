from rest_framework import serializers
from .models import Review
from accounts.models import User
from products.models import SareeProduct
from accounts.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at"]
