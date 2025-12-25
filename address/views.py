from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Address
from .serializers import AddressSerializer


# -------------------------
# ADD ADDRESS
# -------------------------
class AddAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddressSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # If default = true, unset previous defaults
        if request.data.get("is_default", False):
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

        address = serializer.save(user=request.user)

        return Response({
            "message": "Address added successfully",
            "address": AddressSerializer(address).data
        }, status=201)


# -------------------------
# LIST USER ADDRESSES
# -------------------------
class ListAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-created_at")
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)


# -------------------------
# UPDATE ADDRESS
# -------------------------
class UpdateAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=404)

        serializer = AddressSerializer(address, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        if request.data.get("is_default", False):
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

        serializer.save()

        return Response({
            "message": "Address updated",
            "address": serializer.data
        })


# -------------------------
# DELETE ADDRESS
# -------------------------
class DeleteAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=404)

        address.delete()
        return Response({"message": "Address deleted"})
