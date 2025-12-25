from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import razorpay

from .models import Order, Payment
from .serializers import AdminOrderSerializer
from .permissions import IsAdminUser



class AdminOrderListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        orders = Order.objects.all().order_by("-created_at")
        serializer = AdminOrderSerializer(orders, many=True)
        return Response(serializer.data)






class AdminUpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, order_uid):
        status = request.data.get("status")

        if status not in ["PAID", "SHIPPED", "DELIVERED", "CANCELLED"]:
            return Response({"error": "Invalid status"}, status=400)

        try:
            order = Order.objects.get(uid=order_uid)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        order.status = status
        order.save()

        return Response({
            "message": "Order status updated",
            "order_uid": order.uid,
            "status": order.status
        })







class AdminCancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, order_uid):
        try:
            order = Order.objects.get(uid=order_uid)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if order.status in ["DELIVERED", "CANCELLED"]:
            return Response({"error": "Cannot cancel this order"}, status=400)

        order.status = "CANCELLED"
        order.save()

        return Response({"message": "Order cancelled"})



class AdminRefundOrderAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, order_uid):
        try:
            payment = Payment.objects.get(order__uid=order_uid, status="PAID")
        except Payment.DoesNotExist:
            return Response({"error": "Paid payment not found"}, status=404)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            refund = client.payment.refund(
                payment.razorpay_payment_id,
                {"amount": int(payment.amount * 100)}
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        payment.status = "REFUNDED"
        payment.save()

        order = payment.order
        order.status = "CANCELLED"
        order.save()

        return Response({
            "message": "Refund successful",
            "refund_id": refund["id"]
        })
