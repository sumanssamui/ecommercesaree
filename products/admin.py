from django.contrib import admin
from .models import Category, SareeProduct, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class SareeProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "stock", "material", "color")
    inlines = [ProductImageInline]

class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)   # show slug but disable editing
    list_display = ('name', 'slug', 'created_at')

admin.site.register(Category, CategoryAdmin)
admin.site.register(SareeProduct, SareeProductAdmin)
