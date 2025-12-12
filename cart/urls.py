from django.urls import path
from .views import (
    AddToCartAPIView,
    ViewCartAPIView,
    UpdateCartItemAPIView,
    DeleteCartItemAPIView
)

urlpatterns = [
    path('add/', AddToCartAPIView.as_view(), name="add_to_cart"),
    path('view/', ViewCartAPIView.as_view(), name="view_cart"),
    path('update/', UpdateCartItemAPIView.as_view(), name="update_cart"),
    path('delete/<int:item_id>/', DeleteCartItemAPIView.as_view(), name="delete_cart_item"),
]
