from django.db import models
import uuid


# -----------------------
# CATEGORY MODEL
# -----------------------
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Create slug from the name (no random text)
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name





# -----------------------
# PRODUCT MODEL (SAREE)
# -----------------------
class SareeProduct(models.Model):
    MATERIAL_CHOICES = [
        ('Cotton', 'Cotton'),
        ('Silk', 'Silk'),
        ('Banarasi', 'Banarasi'),
        ('Kanjivaram', 'Kanjivaram'),
        ('Linen', 'Linen'),
        ('Soft Silk', 'Soft Silk'),
        ('Designer', 'Designer'),
        ('Other', 'Other'),
    ]

    COLOR_CHOICES = [
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Pink', 'Pink'),
        ('Yellow', 'Yellow'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Other', 'Other'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    color = models.CharField(max_length=50, choices=COLOR_CHOICES)
    stock = models.IntegerField(default=0)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



# -----------------------
# PRODUCT IMAGE MODEL
# -----------------------
class ProductImage(models.Model):
    product = models.ForeignKey(SareeProduct, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/")

    def __str__(self):
        return f"Image for {self.product.title}"
