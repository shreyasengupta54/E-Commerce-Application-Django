import re
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django import forms
from urllib.parse import unquote
from .models import Product, Category, Profile
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserAddressForm
from cart.cart import Cart
from payments.forms import ShippingForm
from payments.models import ShippingAddress

def home(request):
    products = Product.objects.select_related('category__parent').all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            current_user = Profile.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart
            if saved_cart:
                saved_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key, val in saved_cart.items():
                    cart.persist_add(product=key, quantity=val)
            messages.success(request, ("Logged in successfully."))
            return redirect('home')
        else:
            messages.success(request, ("Could not log in. Please try again."))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("Logged out successfully."))
    return redirect('home')

def password_reset(request):
    return render(request, 'about.html', {})

def signup(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password  = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, ("Signed Up and Logged in successfully. Please add your address."))
            return redirect('update_info')
        else:
            messages.success(request, ("Could not Register. Please try again."))
            return redirect('signup')
    else:
        return render(request, 'signup.html', {'form': form})

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})

def category(request, name):
    # Replace hyphens with spaces
    name = unquote(name)
    name = name.replace('-',' ')
    words = name.split()
    capitalized_words = [word.capitalize() if word != 'and' else word for word in words]
    name = ' '.join(capitalized_words)
    # if 'Mens' in name:
    #     name = name.replace('Mens', "Men's")
    # if 'Womens' in name:
    #     name = name.replace('Womens', "Women's")
    print(name)
    try:
        category = Category.objects.get(name=name)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except Exception as e:
        print(str(e))
        messages.success(request, ("Category doesn't exist"))
        return redirect('home')
    
def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, 'User details updated successfully.')
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.success(request, 'Cannot update user without logging in.')
        return redirect('home')
    
def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your Password has been updated. Please log in with new password.')
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})        
    else:
        messages.success(request, 'Cannot update user password without logging in.')
        return redirect('home')
    
def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        form = UserAddressForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            submitted_value = request.POST['submit_action']
            if submitted_value == 'billing':
                form.save()  
                #shipping_form.save()  
                messages.success(request, 'Billing address updated successfully.')
            if submitted_value == 'shipping':
                shipping_form.save()            
                messages.success(request, 'Shipping address updated successfully.')
            return redirect('update_info')
        '''
        if shipping_form.is_valid():
            shipping_form.save()            
            messages.success(request, 'Shipping address updated successfully.')
            return redirect('update_info')
        '''    
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    else:
        messages.success(request, 'Cannot update user address without logging in.')
        return redirect('home')
    
def search(request):
    if request.method == 'POST':
        query = request.POST.get('search')
        q_name = Q(name__icontains=query)
        q_category = Q(category__name__icontains=query) | Q(category__parent__name__icontains=query)
        q_description =  Q(description__icontains=query)
        products = Product.objects.filter(q_name | q_category | q_description)
        if not products:
            messages.success(request, 'No matching products found.')
            return render(request, 'home.html', {'products': Product.objects.select_related('category__parent').all()})
        if query != "":            
            return render(request, 'search.html', {'products': products})
        else:
            #messages.success(request, 'No matching products found.')
            return render(request, 'home.html', {'products': Product.objects.select_related('category__parent').all()})
    else:
        return render(request, 'home.html', {'products': Product.objects.select_related('category__parent').all()})
    