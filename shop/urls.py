from django.urls import path
from . import views

urlpatterns = [
	path('', views.shop, name="shop"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
	path('initiate_payment/', views.initiate_monobank_payment, name='initiate_payment'),
	path('monobank/redirect/', views.monobank_redirect_handler, name='monobank_redirect'),
	path('monobank/webhook/', views.monobank_webhook_handler, name='monobank_webhook'),
	path('product/<int:pk>/', views.product_detail, name="product_detail"),
]