from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Wishlist, WishlistItem
from products.models import SareeProduct
from .serializers import WishlistSerializer


def get_user_wishlist(user):
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    return wishlist


# -------------------------
# ADD TO WISHLIST
# -------------------------
class AddToWishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")

        try:
            product = SareeProduct.objects.get(uid=product_id)
        except SareeProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        wishlist = get_user_wishlist(request.user)

        # Prevent duplicate items
        if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            return Response({"message": "Product already in wishlist"})

        WishlistItem.objects.create(wishlist=wishlist, product=product)

        return Response({"message": "Added to wishlist"})


# -------------------------
# VIEW WISHLIST
# -------------------------
class ViewWishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist = get_user_wishlist(request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)


# -------------------------
# REMOVE ITEM FROM WISHLIST
# -------------------------
class RemoveWishlistItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = WishlistItem.objects.get(id=item_id, wishlist__user=request.user)
        except WishlistItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.delete()
        return Response({"message": "Removed from wishlist"})
