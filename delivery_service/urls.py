from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.products.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('orders/', include('apps.orders.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('courier/', include('apps.courier.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
