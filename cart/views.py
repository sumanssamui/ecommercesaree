from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from products.models import SareeProduct
from .serializers import CartSerializer


# Helper: Get or create user cart
def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


# ----------------------------
# ADD ITEM TO CART
# ----------------------------
class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "product_id required"}, status=400)

        if quantity <= 0:
            return Response({"error": "Quantity must be greater than zero"}, status=400)

        try:
            product = SareeProduct.objects.get(uid=product_id)
        except SareeProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.save()

        return Response({"message": "Item added to cart successfully"}, status=200)



# ----------------------------
# VIEW CART
# ----------------------------
class ViewCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_user_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


# ----------------------------
# UPDATE CART ITEM QUANTITY
# ----------------------------
class UpdateCartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)

        if quantity <= 0:
            cart_item.delete()
            return Response({"message": "Item removed from cart"})

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Cart updated"})


# ----------------------------
# DELETE CART ITEM
# ----------------------------
class DeleteCartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        cart_item.delete()
        return Response({"message": "Item removed successfully"})
