from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include("accounts.urls")),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('reviews/', include('reviews.urls')),
    path('address/', include('address.urls')),
    path('orders/',include("orders.urls")),
    path('admin-api/', include('orders.admin_urls')),

]


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)