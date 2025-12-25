from django.urls import path
from .admin_views import (
    AdminOrderListAPIView,
    AdminUpdateOrderStatusAPIView,
    AdminCancelOrderAPIView,
    AdminRefundOrderAPIView
)

urlpatterns = [
    path('orders/', AdminOrderListAPIView.as_view()),
    path('orders/<uuid:order_uid>/status/', AdminUpdateOrderStatusAPIView.as_view()),
    path('orders/<uuid:order_uid>/cancel/', AdminCancelOrderAPIView.as_view()),
    path('orders/<uuid:order_uid>/refund/', AdminRefundOrderAPIView.as_view()),
]
