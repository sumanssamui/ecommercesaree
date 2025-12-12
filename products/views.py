from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SareeProduct, Category
from .serializers import SareeProductSerializer
from django.db.models import Q


# ---------------------------
# PRODUCT LIST VIEW WITH SORTING
# ---------------------------

from math import ceil


class ProductListAPIView(APIView):
    def get(self, request):
        products = SareeProduct.objects.all()

        # -------------------------
        # EXISTING FILTERS
        # -------------------------
        category = request.GET.get("category")
        if category:
            products = products.filter(category__slug=category)

        material = request.GET.get("material")
        if material:
            products = products.filter(material__iexact=material)

        color = request.GET.get("color")
        if color:
            products = products.filter(color__iexact=color)

        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        search = request.GET.get("search")
        if search:
            products = products.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        # -------------------------
        # SORTING
        # -------------------------
        sort = request.GET.get("sort")

        if sort == "newest":
            products = products.order_by("-created_at")
        elif sort == "oldest":
            products = products.order_by("created_at")
        elif sort == "price_low":
            products = products.order_by("price")
        elif sort == "price_high":
            products = products.order_by("-price")
        else:
            products = products.order_by("-created_at")

        # -------------------------
        # PAGINATION
        # -------------------------
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 12))

        total_products = products.count()
        total_pages = ceil(total_products / limit)

        start = (page - 1) * limit
        end = start + limit

        products = products[start:end]

        serializer = SareeProductSerializer(products, many=True)

        return Response({
            "total_products": total_products,
            "total_pages": total_pages,
            "current_page": page,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
            "limit": limit,
            "results": serializer.data
        })






# SINGLE PRODUCT DETAILS
class ProductDetailAPIView(APIView):
    def get(self, request, uid):
        try:
            product = SareeProduct.objects.get(uid=uid)
        except SareeProduct.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        serializer = SareeProductSerializer(product)
        return Response(serializer.data, status=200)




# add products here
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import SareeProductSerializer, SareeProductCreateSerializer, ProductImageSerializer
from .models import SareeProduct, ProductImage, Category
from rest_framework.permissions import IsAuthenticated


class ProductCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Important for image upload
    # permission_classes = [IsAuthenticated]          # Only logged-in admin can add product

    def post(self, request):
        serializer = SareeProductCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        product = serializer.save()

        # Upload multiple images
        images = request.FILES.getlist('images')

        for img in images:
            ProductImage.objects.create(product=product, image=img)

        return Response({
            "message": "Product Added Successfully",
            "product": SareeProductSerializer(product).data
        }, status=201)
