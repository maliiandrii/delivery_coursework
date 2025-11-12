from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('create/', views.create_order, name='create_order'),
    path('my-orders/', views.order_list_view, name='order_list'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
]
