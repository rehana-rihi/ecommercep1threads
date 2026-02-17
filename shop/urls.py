from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cart/', views.cart_view, name='cart_view'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/sync-cart/', views.sync_cart, name='sync_cart'),
    path('api/get-cart/', views.get_cart, name='get_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('orders/', views.order_history, name='order_history'),
]