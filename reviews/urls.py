from django.urls import path
from .views import (
    AddReviewAPIView,
    UpdateReviewAPIView,
    DeleteReviewAPIView,
    ProductReviewsAPIView
)

urlpatterns = [
    path('<uuid:product_uid>/add/', AddReviewAPIView.as_view(), name="add_review"),
    path('<uuid:product_uid>/update/', UpdateReviewAPIView.as_view(), name="update_review"),
    path('<uuid:product_uid>/delete/', DeleteReviewAPIView.as_view(), name="delete_review"),
    path('<uuid:product_uid>/list/', ProductReviewsAPIView.as_view(), name="product_reviews"),
]
