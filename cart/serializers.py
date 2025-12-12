from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import SareeProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = SareeProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "cart_total"]

    def get_cart_total(self, obj):
        return sum(item.total_price for item in obj.items.all())
