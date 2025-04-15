import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except json.JSONDecodeError:
        cart = {}
        print("Warning: Could not decode cart cookie.")


    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = 0

    for i in cart:
        try:
            quantity = cart[i].get('quantity', 0)

            if quantity > 0:
                product = Product.objects.get(id=i)

                total = (product.price * quantity)

                order['get_cart_total'] += total
                cartItems += quantity

                item = {
                    'product': product,
                    'quantity': quantity,
                    'get_total': total,
                }
                items.append(item)

                if not product.digital:
                    order['shipping'] = True
            else:
                pass

        except Product.DoesNotExist:
            print(f"Warning: Product with ID {i} not found in database (from cookie).")
            pass
        except Exception as e:
            print(f"Error processing cart item ID {i}: {e}")
            pass

    order['get_cart_items'] = cartItems

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
            email=email,
            )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
        )

    for item_data in items:
        product = item_data['product']
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item_data['quantity'],
        )
    return customer, order