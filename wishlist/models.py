from django.db import models
from accounts.models import User
from products.models import SareeProduct


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.email}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(SareeProduct, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('wishlist', 'product')  # Prevent duplicates

    def __str__(self):
        return f"{self.product.title}"
