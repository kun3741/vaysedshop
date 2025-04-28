from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
import requests
import uuid
from .utils import *


def shop(request):
	data = cartData(request)
	cartItems = data['cartItems']
	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'shop/shop.html', context)

def cart(request):
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'shop/cart.html', context)

def checkout(request):
    data = cartData(request)
    if not data['items']:
        return redirect('cart')

    context = {
        'items': data['items'],
        'order': data['order'],
        'cartItems': data['cartItems'],
        'user_authenticated': request.user.is_authenticated,
        'shipping': data['order']['shipping']
    }
    return render(request, 'shop/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = None
	if request.user.is_authenticated:
		customer = request.user.customer
	else:
		pass

	if customer:
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

	return JsonResponse('Item was added/updated', safe=False)



def initiate_monobank_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        frontend_data = json.loads(request.body)
        shipping_info = frontend_data.get('shipping')
        user_form_data = frontend_data.get('user')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    cart_info = cartData(request)
    items = cart_info['items']
    order_details = cart_info['order']

    if not items:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    order = None
    customer = None
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order.orderitem_set.all().delete()
        for item_data in items:
             OrderItem.objects.create(
                 product=item_data['product'],
                 order=order,
                 quantity=item_data['quantity']
             )
    else:
        guest_name = user_form_data.get('name')
        guest_email = user_form_data.get('email')
        guest_phone = user_form_data.get('phone')

        if not guest_name or not guest_phone:
            return JsonResponse({'error': 'Name and Phone number are required for guest checkout'}, status=400)

        customer_identifier = guest_email if guest_email else f"guest_{guest_phone}_{uuid.uuid4()}"

        customer, created = Customer.objects.update_or_create(
            email=customer_identifier, 
            defaults={'name': guest_name, 'phone': guest_phone}
        )

        order = Order.objects.create(customer=customer, complete=False)
        for item_data in items:
            OrderItem.objects.create(
                product=item_data['product'],
                order=order,
                quantity=item_data['quantity']
            )

    if order_details['shipping'] and shipping_info:
        ShippingAddress.objects.update_or_create(
            customer=customer,
            order=order,
            defaults={
                'phone': shipping_info.get('guest_phone', ''),
                'address': shipping_info.get('address', ''),
                'city': shipping_info.get('city', ''),
                'state': shipping_info.get('state', ''),
                'zipcode': shipping_info.get('zipcode', '')
            }
        )

    total_amount_kopecks = int(order.get_cart_total * 100)
    if total_amount_kopecks <= 0:
         return JsonResponse({'error': 'Total amount must be positive'}, status=400)

    mono_api_url = "https://api.monobank.ua/api/merchant/invoice/create"
    mono_token = settings.MONOBANK_API_TOKEN

    if not mono_token:
        print("ERROR: Monobank API token is not configured in settings.py")
        return JsonResponse({'error': 'Payment gateway configuration error.'}, status=500)

    headers = {
        "X-Token": mono_token,
        "Content-Type": "application/json"
    }

    merchant_order_id = f"{order.id}-{uuid.uuid4()}"
    redirect_url = request.build_absolute_uri(reverse('monobank_redirect'))
    webhook_url = request.build_absolute_uri(reverse('monobank_webhook'))

    payload = {
        "amount": total_amount_kopecks,
        "merchantPaymInfo": {
            "reference": str(order.id),
            "destination": "Payment in Vaysed Shop",
            "comment": f"Order #{order.id}",
             "basketOrder": [{
                "name": item.product.name,
                "qty": item.quantity,
                "sum": int(item.get_total * 100),
                "icon": request.build_absolute_uri(item.product.image.url) if item.product.image else None,
                "unit": "pcs.",
                 "code": str(item.product.id),
            } for item in order.orderitem_set.all()]
        },
        "redirectUrl": redirect_url,
        "webHookUrl": webhook_url,
        "validity": 3600,
    }

    try:
        response = requests.post(mono_api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        mono_data = response.json()

        order.monobank_invoice_id = mono_data.get('invoiceId')
        order.save()

        print(f"Monobank invoice created: {order.monobank_invoice_id} for Order ID: {order.id}")

        return JsonResponse({'pageUrl': mono_data.get('pageUrl')})

    except requests.exceptions.RequestException as e:
        print(f"Error calling Monobank API: {e}")
        error_message = "Failed to create invoice"
        if hasattr(e, 'response') and e.response is not None:
            try:
                 error_details = e.response.json()
                 print(f"Monobank API Error Details: {error_details}")
                 error_message = error_details.get('errText', 'Failed to create invoice')
            except json.JSONDecodeError:
                 error_message = f"Failed to create invoice (Status: {e.response.status_code})"
        else:
            error_message = "Failed to create invoice due to network error or timeout."
        return JsonResponse({"error": error_message}, status=500)

    except Exception as e:
        print(f"Unexpected error during payment initiation: {e}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)


def monobank_redirect_handler(request):

    order = None
    items = []
    shipping_address = None
    message = "Thank you for your order!"
    error_message = None

    try:
        order = Order.objects.latest('date_ordered')
        items = order.orderitem_set.prefetch_related('product').all()
        shipping_address = ShippingAddress.objects.filter(order=order).first()

    except Order.DoesNotExist:
        error_message = "There are no orders in the system yet."
        message = "Display Error"
    except Exception as e:
        print(f"Error in super simplified handler: {e}")
        error_message = "An unexpected error occurred while searching for the last order."
        message = "Display Error"
        order = None

    context = {
        'message': message,
        'error_message': error_message,
        'order': order,
        'items': items,
        'shipping_address': shipping_address,
    }

    response = render(request, 'shop/payment_result.html', context)

    response.delete_cookie('cart', path='/')

    return response

@csrf_exempt
def monobank_webhook_handler(request):
    if request.method != 'POST':
        print("Webhook: Received non-POST request")
        return HttpResponse(status=405)


    try:
        data = json.loads(request.body)
        invoice_id = data.get('invoiceId')
        status = data.get('status')
        amount = data.get('amount')
        ccy = data.get('ccy')

        print(f"Webhook received: invoiceId={invoice_id}, status={status}, amount={amount}, ccy={ccy}")

        if not invoice_id or not status:
             print("Webhook: Missing invoiceId or status in payload")
             return HttpResponse(status=400)

        try:
            order = Order.objects.get(monobank_invoice_id=invoice_id)

            if order.complete:
                print(f"Webhook: Order {order.id} (Invoice: {invoice_id}) is already marked as complete.")
                return HttpResponse(status=200)

            if status == 'success':
                expected_amount_kopecks = int(order.get_cart_total * 100)
                if amount == expected_amount_kopecks and ccy == 980:
                    order.complete = True
                    order.transaction_id = f"mono_{invoice_id}"
                    order.save()
                    print(f"Webhook: Order {order.id} (Invoice: {invoice_id}) marked as complete.")


                else:
                    print(f"Webhook SECURITY WARNING: Amount mismatch for order {order.id}. Expected {expected_amount_kopecks}, got {amount}. Currency: {ccy}")

            elif status in ['failure', 'expired']:
                print(f"Webhook: Payment failed or expired for order {order.id} (Invoice: {invoice_id}). Status: {status}")
            else:
                print(f"Webhook: Received intermediate status '{status}' for order {order.id}")

            return HttpResponse(status=200)

        except Order.DoesNotExist:
            print(f"Webhook Error: Order with invoiceId {invoice_id} not found.")
            return HttpResponse(status=200)
        except Exception as e:
            print(f"Webhook Error: Error processing webhook for invoice {invoice_id}: {e}")
            return HttpResponse(status=500)

    except json.JSONDecodeError:
        print("Webhook Error: Invalid JSON received")
        return HttpResponse(status=400)
    except Exception as e:
        print(f"Webhook Error: Unexpected error in webhook handler: {e}")
        return HttpResponse(status=500)


def product_detail(request, pk):
	product = get_object_or_404(Product, pk=pk)
	data = cartData(request)
	cartItems = data['cartItems']
	context = {'product': product, 'cartItems': cartItems}
	return render(request, 'shop/product_detail.html', context)