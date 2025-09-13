from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('excursions/', views.excursions, name='excursions'),
    path('delivery/', views.delivery, name='delivery'),
    path('products/', views.products, name='products'),
    path('candles/', views.candles, name='candles'),
    path('contacts/', views.contacts, name='contacts'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart, name='cart'),
    # cart ops
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/qty/<str:op>/<int:product_id>/', views.change_qty, name='change_qty'),
    # order ops
    path('order/create/', views.create_order, name='create_order'),
]