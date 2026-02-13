from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import SareeProductSerializer
from products.models import SareeProduct
from django.db.models import Sum
from django.utils import timezone





class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SareeProduct
        fields = ["id", "title"]



class OrderItemSerializer(serializers.ModelSerializer):
    # product = SareeProductSerializer(read_only=True)
    product = OrderProductSerializer(read_only=True)


    class Meta:
        model = OrderItem
        fields = ["product", "price", "quantity", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    payment_status = serializers.CharField(source="payment.status", read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "uid",
            "total_amount",
            "status",
            "payment_status",
            "total_items",
            "is_expired",
            "created_at",
            "items"
        ]

    # def get_total_items(self, obj):
    #     return obj.items.aggregate(
    #         total=models.Sum("quantity")
    #     )["total"] or 0
    
    def get_total_items(self, obj):
        return obj.items.aggregate(
            total=Sum("quantity")
        )["total"] or 0


    def get_is_expired(self, obj):
        if obj.expires_at:
            return obj.expires_at < timezone.now()
        return False







class AdminOrderItemSerializer(serializers.ModelSerializer):
    product = SareeProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "price", "quantity", "total_price"]


class AdminOrderSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    payment_status = serializers.CharField(source="payment.status", read_only=True)
    razorpay_payment_id = serializers.CharField(
        source="payment.razorpay_payment_id",
        read_only=True
    )
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "uid",
            "user",
            "user_email",
            "address",
            "total_amount",
            "status",
            "payment_status",
            "razorpay_payment_id",
            "created_at",
            "updated_at",
            "items"
        ]

