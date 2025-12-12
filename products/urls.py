from django.urls import path
from .views import ProductListAPIView, ProductDetailAPIView , ProductCreateAPIView

urlpatterns = [
    path('', ProductListAPIView.as_view(), name='product_list'),
    path('add/', ProductCreateAPIView.as_view(), name='add_product'),
    path('<uuid:uid>/', ProductDetailAPIView.as_view(), name='product_detail'),
]
