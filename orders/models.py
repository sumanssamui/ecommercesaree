from django.db import models
from accounts.models import User
from products.models import SareeProduct
from address.models import Address
import uuid


class Order(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    )

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.PROTECT)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.uid} - {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(SareeProduct, on_delete=models.PROTECT)

    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at order time
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="CREATED")  # CREATED, PAID, FAILED
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.order.uid}"
