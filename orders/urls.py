from django.urls import path
from .views import (
    CreateOrderAPIView,
    MyOrdersAPIView,
    CreateRazorpayOrderAPIView,
    VerifyRazorpayPaymentAPIView,
    CheckoutAPIView,
    OrderInvoiceDownloadAPIView
)

urlpatterns = [
    path('create/', CreateOrderAPIView.as_view()),
    path('my-orders/', MyOrdersAPIView.as_view()),
    path('<uuid:order_uid>/razorpay/', CreateRazorpayOrderAPIView.as_view()),
    path('verify-payment/', VerifyRazorpayPaymentAPIView.as_view()),
    path('checkout/', CheckoutAPIView.as_view()),
    path('<uuid:order_uid>/invoice/', OrderInvoiceDownloadAPIView.as_view()),
]




