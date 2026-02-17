from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Order
from django.utils import timezone

def index(request):
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

def cart_view(request):
    return render(request, 'shop/cart.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to P1/Threads!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('index')

# NEW: API endpoints for cart sync
def sync_cart(request):
    """Sync localStorage cart with database cart"""
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            # Get cart data from request
            data = json.loads(request.body)
            cart_items = data.get('cart', [])
            
            # Get or create user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Clear existing items
            cart.items.all().delete()
            
            # Add new items
            for item in cart_items:
                product = Product.objects.get(id=item['id'])
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=item['quantity']
                )
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def get_cart(request):
    """Get user's cart from database"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            items = []
            for item in cart.items.all():
                items.append({
                    'id': item.product.id,
                    'title': item.product.title,
                    'price': float(item.product.price),
                    'quantity': item.quantity,
                    'image': item.product.image
                })
            return JsonResponse({'cart': items})
        except Cart.DoesNotExist:
            return JsonResponse({'cart': []})
    
    return JsonResponse({'cart': []})
@login_required
def checkout_view(request):
    return render(request, 'shop/checkout.html')

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            # Get cart data from form
            cart_data = request.POST.get('cart_data')
            if not cart_data:
                return JsonResponse({'status': 'error', 'message': 'No cart data'})
            
            # Parse cart data
            cart_items = json.loads(cart_data)
            
            if not cart_items:
                return JsonResponse({'status': 'error', 'message': 'Cart is empty'})
            
            # Calculate total
            total_amount = 0
            for item in cart_items:
                total_amount += float(item['price']) * int(item['quantity'])
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                status='Confirmed'
            )
            
            # Create cart items and associate with order
            for item in cart_items:
                product = Product.objects.get(id=item['id'])
                cart_item = CartItem.objects.create(
                    cart=None,  # Set cart to None for order items
                    product=product,
                    quantity=item['quantity']
                )
                order.items.add(cart_item)
            
            return JsonResponse({
                'status': 'success', 
                'order_id': order.id,
                'message': 'Order placed successfully!'
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})