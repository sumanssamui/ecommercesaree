from django.db import models
from accounts.models import User
from products.models import SareeProduct
from address.models import Address
import uuid


from django.utils import timezone
from datetime import timedelta

class Order(models.Model):

    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        PAYMENT_PENDING = "PAYMENT_PENDING", "Payment Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        EXPIRED = "EXPIRED", "Expired"

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        db_index=True
    )

    address = models.ForeignKey(Address, on_delete=models.PROTECT)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True
    )

    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def mark_expired(self):
        if self.status == self.Status.PAYMENT_PENDING:
            self.status = self.Status.EXPIRED
            self.save(update_fields=["status"])

    def __str__(self):
        return f"Order {self.uid} - {self.user.email}"



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        SareeProduct,
        on_delete=models.PROTECT
    )

    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"



class Payment(models.Model):

    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        AUTHORIZED = "AUTHORIZED", "Authorized"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True
    )

    failure_reason = models.TextField(blank=True, null=True)

    raw_response = models.JSONField(blank=True, null=True)  # store full gateway response

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Payment {self.status} - {self.order.uid}"

