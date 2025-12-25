from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Review
from products.models import SareeProduct
from .serializers import ReviewSerializer


# -----------------------------
# ADD REVIEW
# -----------------------------
class AddReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_uid):
        rating = int(request.data.get("rating", 1))
        comment = request.data.get("comment", "")

        if rating < 1 or rating > 5:
            return Response({"error": "Rating must be between 1 and 5"}, status=400)

        try:
            product = SareeProduct.objects.get(uid=product_uid)
        except SareeProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        # Prevent duplicate review
        if Review.objects.filter(user=request.user, product=product).exists():
            return Response({"error": "You already reviewed this product"}, status=400)

        review = Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment
        )

        return Response({
            "message": "Review added successfully",
            "review": ReviewSerializer(review).data
        }, status=201)


# -----------------------------
# UPDATE REVIEW
# -----------------------------
class UpdateReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, product_uid):
        rating = int(request.data.get("rating", 1))
        comment = request.data.get("comment", "")

        try:
            product = SareeProduct.objects.get(uid=product_uid)
            review = Review.objects.get(user=request.user, product=product)
        except:
            return Response({"error": "Review not found"}, status=404)

        review.rating = rating
        review.comment = comment
        review.save()

        return Response({
            "message": "Review updated",
            "review": ReviewSerializer(review).data
        })


# -----------------------------
# DELETE REVIEW
# -----------------------------
class DeleteReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_uid):
        try:
            product = SareeProduct.objects.get(uid=product_uid)
            review = Review.objects.get(user=request.user, product=product)
        except:
            return Response({"error": "Review not found"}, status=404)

        review.delete()
        return Response({"message": "Review deleted"})


# -----------------------------
# LIST PRODUCT REVIEWS
# -----------------------------
class ProductReviewsAPIView(APIView):
    def get(self, request, product_uid):
        try:
            product = SareeProduct.objects.get(uid=product_uid)
        except SareeProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        reviews = Review.objects.filter(product=product).order_by("-created_at")
        serializer = ReviewSerializer(reviews, many=True)

        # calculate average rating
        avg = reviews.aggregate(avg_rating=models.Avg("rating"))["avg_rating"]

        return Response({
            "average_rating": round(avg, 1) if avg else 0,
            "total_reviews": reviews.count(),
            "reviews": serializer.data
        })
