from rest_framework import serializers
from .models import Wishlist, WishlistItem
from products.serializers import SareeProductSerializer


class WishlistItemSerializer(serializers.ModelSerializer):
    product = SareeProductSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product"]


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "items"]
