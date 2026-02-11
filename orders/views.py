from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from decimal import Decimal
from django.db import transaction
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from address.models import Address
from .serializers import OrderSerializer

import razorpay
from django.conf import settings
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart, CartItem
from address.models import Address
from .models import Order, OrderItem, Payment
from .utils.invoice import generate_invoice_pdf
from .utils.email_service import send_order_confirmation_email

import os
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Order





# class CreateOrderAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         address_id = request.data.get("address_id")

#         # Validate address
#         try:
#             address = Address.objects.get(id=address_id, user=user)
#         except Address.DoesNotExist:
#             return Response({"error": "Invalid address"}, status=400)

#         # Get cart
#         try:
#             cart = Cart.objects.get(user=user)
#         except Cart.DoesNotExist:
#             return Response({"error": "Cart is empty"}, status=400)

#         cart_items = CartItem.objects.filter(cart=cart)
#         if not cart_items.exists():
#             return Response({"error": "Cart is empty"}, status=400)

#         total_amount = Decimal("0.00")

#         # Create Order
#         order = Order.objects.create(
#             user=user,
#             address=address,
#             total_amount=0
#         )

#         # Create Order Items
#         for item in cart_items:
#             product = item.product

#             if item.quantity > product.stock:
#                 order.delete()
#                 return Response({
#                     "error": f"{product.title} is out of stock"
#                 }, status=400)

#             price = product.discount_price or product.price
#             item_total = price * item.quantity
#             total_amount += item_total

#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 price=price,
#                 quantity=item.quantity,
#                 total_price=item_total
#             )

#             # Reduce stock
#             product.stock -= item.quantity
#             product.save()

#         order.total_amount = total_amount
#         order.save()

#         # Clear cart
#         cart_items.delete()

#         return Response({
#             "message": "Order created successfully",
#             "order": OrderSerializer(order).data
#         }, status=201)


class MyOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)










import razorpay
from django.conf import settings
from .models import Payment
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


class CreateRazorpayOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_uid):
        try:
            order = Order.objects.get(uid=order_uid, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if order.status != "PENDING":
            return Response({"error": "Order already paid"}, status=400)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            "amount": int(order.total_amount * 100),  # INR → paise
            "currency": "INR",
            "payment_capture": 1
        })

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "razorpay_order_id": razorpay_order["id"],
                "amount": order.total_amount
            }
        )

        # If payment already exists, update razorpay order id
        if not created:
            payment.razorpay_order_id = razorpay_order["id"]
            payment.amount = order.total_amount
            payment.save()


        return Response({
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": int(order.total_amount * 100),
            "currency": "INR"
        })







class VerifyRazorpayPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        try:
            payment = Payment.objects.select_for_update().get(
                razorpay_order_id=razorpay_order_id
            )
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found"}, status=404)

        # ✅ Idempotency protection
        if payment.status == "PAID":
            return Response({"message": "Already verified"}, status=200)

        # ✅ Security check
        if payment.order.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            payment.status = "FAILED"
            payment.save()
            return Response({"error": "Payment verification failed"}, status=400)

        # ✅ Deduct stock safely
        order = payment.order
        # order_items = OrderItem.objects.select_related("product").filter(order=order)
        order_items = OrderItem.objects.select_related("product").select_for_update().filter(order=order)


        for item in order_items:
            product = item.product

            if product.stock < item.quantity:
                return Response(
                    {"error": f"{product.title} is out of stock"},
                    status=400
                )

            # product.stock -= item.quantity
            # product.save()
            product.stock = F("stock") - item.quantity
            product.save(update_fields=["stock"])


        # ✅ Mark payment + order
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "PAID"
        payment.save()

        order.status = "PAID"
        order.save()

        # ✅ Clear cart NOW
        CartItem.objects.filter(cart__user=order.user).delete()

        # ✅ Generate invoice + send email
        invoice_path = generate_invoice_pdf(order)
        send_order_confirmation_email(
            user_email=order.user.email,
            invoice_path=invoice_path,
            order_uid=order.uid
        )

        return Response({
            "message": "Payment successful & invoice emailed",
            "order_uid": order.uid
        })


       


class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        address_id = request.data.get("address_id")

        # 1️⃣ Validate address
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid address"}, status=400)

        # 2️⃣ Get cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart is empty"}, status=400)

        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        # 3️⃣ Create Order
        total_amount = Decimal("0.00")
        order = Order.objects.create(
            user=user,
            address=address,
            total_amount=0,
            status="PENDING"
        )

        # 4️⃣ Create Order Items
        for item in cart_items:
            product = item.product

            if item.quantity > product.stock:
                order.delete()
                return Response({
                    "error": f"{product.title} is out of stock"
                }, status=400)

            price = product.discount_price or product.price
            item_total = price * item.quantity
            total_amount += item_total

            OrderItem.objects.create(
                order=order,
                product=product,
                price=price,
                quantity=item.quantity,
                total_price=item_total
            )


        order.total_amount = total_amount
        order.save()

        # 5️⃣ Create Razorpay Order
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            "amount": int(total_amount * 100),  # INR → paise
            "currency": "INR",
            "payment_capture": 1
        })

        # Payment.objects.create(
        #     order=order,
        #     razorpay_order_id=razorpay_order["id"],
        #     amount=total_amount
        # )

        Payment.objects.get_or_create(
            order=order,
            defaults={
                "razorpay_order_id": razorpay_order["id"],
                "amount": total_amount
            }
        )


        # 7️⃣ Return payment payload to frontend
        return Response({
            "message": "Checkout initiated",
            "order_uid": order.uid,
            "razorpay": {
                "key": settings.RAZORPAY_KEY_ID,
                "order_id": razorpay_order["id"],
                "amount": int(total_amount * 100),
                "currency": "INR"
            }
        }, status=201)



class OrderInvoiceDownloadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_uid):
        try:
            order = Order.objects.get(uid=order_uid)
        except Order.DoesNotExist:
            # raise Http404("Order not found")  # ✅ RAISE, not return
            # return Http404("Order not found")
            raise Http404("Order not found")


        # Permission check:
        # user can download own invoice
        # admin can download any invoice
        if order.user != request.user and not request.user.is_staff:
            raise Http404("Not allowed")

        invoice_path = os.path.join(
            settings.MEDIA_ROOT,
            "invoices",
            f"invoice_{order.uid}.pdf"
        )

        if not os.path.exists(invoice_path):
            raise Http404("Invoice not found")

        return FileResponse(
            open(invoice_path, "rb"),
            as_attachment=True,
            filename=f"invoice_{order.uid}.pdf"
        )
