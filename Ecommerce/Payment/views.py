from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import razorpay

from .models import Order, Payment
from Cart.models import CartItem


def bill_detail(request):
    user = request.user

    cart_items = CartItem.objects.filter(cart__user=user)  # Get all cart items

    if not cart_items.exists():
        messages.error(request, "No items in the cart!")
        return redirect('cart')

    # Get or create the order for ALL cart items.  Important change!
    orders = []
    for cart_item in cart_items:
        order, created = Order.objects.get_or_create(user=user, cart_item=cart_item)
        orders.append(order)


    if request.method == 'POST':
        name = request.POST.get('name')
        state = request.POST.get('state')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        for order in orders: # Update all orders
            order.name = name
            order.state = state
            order.address = address
            order.city = city
            order.postcode = postcode
            order.phone = phone
            order.email = email
            order.save()

        messages.success(request, "Order details updated successfully!") #More accurate message
        return redirect('checkout')

    return render(request, "Payment/bill_detail.html", {'orders': orders, 'cart_items': cart_items}) #Pass all orders and cart items


def checkout(request):
    user = request.user

    cart_items = CartItem.objects.filter(cart__user=user)

    total_amount = sum(int(item.total_price() * 100) for item in cart_items)

    if total_amount <= 0:
        messages.error(request, "Your cart is empty or invalid!")
        return redirect("cart")

    orders = Order.objects.filter(user=user, cart_item__cart__user=user)

    client = razorpay.Client(auth=('rzp_test_WMKKt2Iww3vC9k', 'eOtrpSH1Y9Z3INB0ULRuqNYn'))

    data = {"amount": total_amount, "currency": "INR", "payment_capture": 1}

    try:
        payment = client.order.create(data=data)
        print("************")
        print(payment)
        print("************")
    except razorpay.errors.BadRequestError as e:
        print("Razorpay Error:", e)
        messages.error(request, "Payment gateway error. Please try again later.")
        return redirect("cart")

    # Associate the Razorpay order_id with ALL orders
    for order in orders:
        order.order_id = payment['id']
        order.save()

    context = {
        "cart_items": cart_items,
        "orders": orders,
        "payment": payment
    }

    return render(request, "Payment/checkout.html", context)


def success(request):
    user = request.user
    cart_items = CartItem.objects.filter(cart__user=user)
    orders = Order.objects.filter(user=user, cart_item__cart__user=user)

    if not orders.exists():
        messages.error(request, "No orders found for this user!")
        return redirect("cart")

    orders.update(status="SUCCESS")  # Update all orders at once

    for order in orders:
        Payment.objects.create(
            user=order.user,
            order_id=order.order_id,
            name=order.name, #No need for hasattr check now
            status="SUCCESS",
        )
        order.delete()  # Delete each order after payment record is created

    cart_items.delete()

    return render(request, "Payment/success.html")  # Removed redundant {"payment": payment}