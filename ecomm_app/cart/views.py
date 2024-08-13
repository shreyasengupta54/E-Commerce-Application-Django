from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    quantities = cart.get_quantities()
    totals = cart.get_cart_total()
    return render(request, 'cart_summary.html', {'cart_products': cart_products, "quantities": quantities, 'totals': totals})

def cart_add(request):
    cart = Cart(request)
    #print(cart.__len__())
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)
        cart.add(product=product, quantity=product_qty)
        messages.success(request, ("Added to Cart."))
        cart_quantity = cart.__len__()
        # response = JsonResponse({'Product Name': product.name})
        response = JsonResponse({'c_qty': cart_quantity, 'Product Name': product.name})
        return response

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product_id)
        messages.success(request, ("Deleted from Cart."))
        response = JsonResponse({'removed product with id': product_id})
        print(response)
        return response

def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        cart.update(product=product_id, quantity=product_qty)
        messages.success(request, ("Updated Quantity."))
        response = JsonResponse({'updated_qty': product_qty})
        print(response)
        return response    