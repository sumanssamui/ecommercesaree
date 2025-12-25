from django.db import models
from accounts.models import User
from products.models import SareeProduct


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(SareeProduct, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(default=1)   # 1 to 5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent multiple reviews per product

    def __str__(self):
        return f"{self.user.email} → {self.product.title} ({self.rating}⭐)"
