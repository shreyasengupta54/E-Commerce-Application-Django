from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from cart.cart import Cart
from payments.forms import ShippingForm, PaymentForm
from payments.models import ShippingAddress, Order, OrderItems
from store.models import Product

def payment_success(request):
    return render(request, 'payments/payment_success.html', {})

def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    quantities = cart.get_quantities()
    totals = cart.get_cart_total()
    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, 'payments/checkout.html', {'cart_products': cart_products, "quantities": quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        shipping_form = ShippingForm(request.POST or None)
        return render(request, 'payments/checkout.html', {'cart_products': cart_products, "quantities": quantities, 'totals': totals, 'shipping_form': shipping_form})

def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_products()
        quantities = cart.get_quantities()
        totals = cart.get_cart_total()
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        if request.user.is_authenticated:
            billing_form = PaymentForm()
            return render(request, 'payments/billing_info.html', {'cart_products': cart_products, "quantities": quantities, 'totals': totals, 'billing_form': billing_form})
        else:
            billing_form = PaymentForm()
            return render(request, 'payments/billing_info.html', {'cart_products': cart_products, "quantities": quantities, 'totals': totals, 'billing_form': billing_form})
    else:
        messages.success(request, "Access Denied.")
        return redirect('home')
    
def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_products()
        quantities = cart.get_quantities()
        payment_form = PaymentForm(request.POST or None)
        my_shipping = request.session.get('my_shipping')
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_pincode']}\n{my_shipping['shipping_country']}"
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        amount_paid = cart.get_cart_total()
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                for k,v in quantities.items():
                    if int(k) == product.id:
                        create_order_item = OrderItems(order_id=order_id, products_id=product_id, user_id=user.id, quantity=v, price=price)
                        create_order_item.save()                        
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]
            messages.success(request, "Order Placed Successfully.")
            return redirect('home')
        else:
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                for k,v in quantities.items():
                    if int(k) == product.id:
                        create_order_item = OrderItems(order_id=order_id, products_id=product_id, quantity=v, price=price)
                        create_order_item.save()                       
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]
            messages.success(request, "Order Placed Successfully.")
            return redirect('home')
    else:
        messages.success(request, "Access Denied.")
        return redirect('home')