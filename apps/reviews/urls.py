from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list_view, name='review_list'),
    path('create/<int:order_id>/', views.create_review, name='create_review'),
]
