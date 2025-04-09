from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import *
import json
import requests
import datetime

def shop(request):
	 
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}
		cartItems = order['get_cart_items']
		
	context = {'items':items, 'order':order}
	 
	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'shop/shop.html', context)

def cart(request):

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items  
		
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'shop/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    if request.method == 'POST':
        total_amount = int(order.get_cart_total * 100)
        order_id = f"order_{order.id}"

        url = "https://api.monobank.ua/api/merchant/invoice/create"
        headers = {
            "X-Token": "ur8zC5CFjp7nRvHpIy7js1qr1N67DEeWRtOLNgxhSjss",
            "Content-Type": "application/json"
        }
        payload = {
            "amount": total_amount,
            "merchantInvoiceId": order_id,
            "redirectUrl": request.build_absolute_uri('/payment_success/'),
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            payment_data = response.json()
            return JsonResponse({'pageUrl': payment_data['pageUrl']}, safe=False)
        else:
            return JsonResponse({"error": "Failed to create invoice"}, status=response.status_code)

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'shop/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()
	return JsonResponse('Item was added', safe=False)

def create_invoice(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        total_amount = data['total_amount']
        order_id = data['order_id']

        url = "https://api.monobank.ua/api/merchant/invoice/create"
        headers = {
            "X-Token": "your_monobank_api_token",
            "Content-Type": "application/json"
        }
        payload = {
            "amount": total_amount,
            "merchantInvoiceId": order_id,
            "redirectUrl": "https://your-redirect-url.com/success",
            "webHookUrl": "https://your-webhook-url.com/webhook"
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({"error": "Failed to create invoice"}, status=response.status_code)

def payment_success(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        if order:
            order.complete = True
            order.save()
            shipping_address = ShippingAddress.objects.filter(order=order).first()
        else:
            order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
            shipping_address = None

        context = {
            'order': order,
            'customer': customer,
            'shipping_address': shipping_address,
        }
        return render(request, 'shop/payment_success.html', context)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    else:
        print('User is not logged in')

    return JsonResponse('Payment submitted..', safe=False)

def product_detail(request, pk):
	product = get_object_or_404(Product, pk=pk)
	context = {'product': product}
	return render(request, 'shop/product_detail.html', context)
