from django.urls import path
from .views import (
    AddAddressAPIView,
    ListAddressAPIView,
    UpdateAddressAPIView,
    DeleteAddressAPIView
)

urlpatterns = [
    path('add/', AddAddressAPIView.as_view()),
    path('list/', ListAddressAPIView.as_view()),
    path('update/<int:address_id>/', UpdateAddressAPIView.as_view()),
    path('delete/<int:address_id>/', DeleteAddressAPIView.as_view()),
]
