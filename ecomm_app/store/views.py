from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Product

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
    return render(request, 'about.html', {})