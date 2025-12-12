from django.urls import path
from .views import (
    AddToWishlistAPIView,
    ViewWishlistAPIView,
    RemoveWishlistItemAPIView
)

urlpatterns = [
    path('add/', AddToWishlistAPIView.as_view(), name="add_wishlist"),
    path('view/', ViewWishlistAPIView.as_view(), name="view_wishlist"),
    path('remove/<int:item_id>/', RemoveWishlistItemAPIView.as_view(), name="remove_wishlist"),
]
