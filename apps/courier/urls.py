from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.courier_orders_view, name='courier_orders'),
    path('accept/<int:order_id>/', views.accept_order, name='accept_order'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
