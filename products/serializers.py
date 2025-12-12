from rest_framework import serializers
from .models import Category, SareeProduct, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


# READ SERIALIZER (for listing)
class SareeProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = SareeProduct
        fields = [
            "uid", "title", "description", "price", "discount_price",
            "material", "color", "stock", "category", "images", "created_at"
        ]


# WRITE SERIALIZER (for add product)
class SareeProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SareeProduct
        fields = [
            "title",
            "description",
            "price",
            "discount_price",
            "material",
            "color",
            "stock",
            "category"
        ]
