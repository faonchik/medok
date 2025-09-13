from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main.views import product_cards

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('admin/product_cards/', product_cards, name='product_cards'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
