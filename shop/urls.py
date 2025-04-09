from django.urls import path

from . import views

urlpatterns = [
	path('', views.shop, name="shop"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('checkout/', views.checkout, name="checkout"),
    path('payment_success/', views.payment_success, name="payment_success"),
    path('process_order/', views.processOrder, name="process_order"),
    path('product/<int:pk>/', views.product_detail, name="product_detail"),
]