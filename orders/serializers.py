from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import SareeProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = SareeProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "price", "quantity", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "uid",
            "total_amount",
            "status",
            "created_at",
            "items"
        ]







class AdminOrderItemSerializer(serializers.ModelSerializer):
    product = SareeProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "price", "quantity", "total_price"]


class AdminOrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    address = serializers.StringRelatedField()
    items = AdminOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "uid",
            "user",
            "address",
            "total_amount",
            "status",
            "created_at",
            "items"
        ]
