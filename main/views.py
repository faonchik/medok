from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from .models import HoneyProduct, WaxCandle, UserProfile, Cart, CartItem, Order, OrderItem
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, OrderForm

# Для админки - карточки товаров
@staff_member_required
def product_cards(request):
    products = HoneyProduct.objects.filter(is_active=True).order_by('-is_featured', '-created_at')
    return render(request, 'admin/product_cards.html', {
        'products': products
    })

# Для основного сайта
def index(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def excursions(request):
    return render(request, 'main/excursions.html')

def delivery(request):
    return render(request, 'main/delivery.html')

def products(request):
    # Здесь можно тоже выводить товары, но для обычных пользователей
    products = HoneyProduct.objects.filter(is_active=True)
    return render(request, 'main/products.html', {'products': products})

def candles(request):
    # Страница восковых свечей
    candles = WaxCandle.objects.filter(is_active=True)
    return render(request, 'main/candles.html', {'candles': candles})

# --------------------------- CART (user based) ---------------------------
def _get_cart(session):
    """Получить корзину из сессии (для совместимости)"""
    cart = session.get('cart', {})
    return cart

def _get_or_create_cart(user):
    """Получить или создать корзину для пользователя"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

def _migrate_session_cart_to_user_cart(user, session):
    """Перенести корзину из сессии в корзину пользователя"""
    session_cart = session.get('cart', {})
    if not session_cart:
        return
    
    cart = _get_or_create_cart(user)
    
    for product_id_str, qty in session_cart.items():
        try:
            product_id = int(product_id_str)
            product = HoneyProduct.objects.get(id=product_id, is_active=True)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': int(qty)}
            )
            
            if not created:
                cart_item.quantity = int(qty)
                cart_item.save()
                
        except (ValueError, HoneyProduct.DoesNotExist):
            continue
    
    # Очищаем корзину из сессии после переноса
    if 'cart' in session:
        del session['cart']
        session.modified = True

@login_required
def add_to_cart(request: HttpRequest, product_id: int):
    """Добавить товар в корзину пользователя"""
    try:
        product = HoneyProduct.objects.get(id=product_id, is_active=True)
        cart = _get_or_create_cart(request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, 'Товар добавлен в корзину')
    except HoneyProduct.DoesNotExist:
        messages.error(request, 'Товар не найден')
    
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

@login_required
def remove_from_cart(request: HttpRequest, product_id: int):
    """Удалить товар из корзины пользователя"""
    try:
        cart = _get_or_create_cart(request.user)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        messages.success(request, 'Товар удален из корзины')
    except Exception as e:
        messages.error(request, 'Ошибка при удалении товара')
    
    return redirect('cart')

@login_required
def change_qty(request: HttpRequest, product_id: int, op: str):
    """Изменить количество товара в корзине"""
    try:
        cart = _get_or_create_cart(request.user)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        
        if op == 'inc':
            cart_item.quantity += 1
        elif op == 'dec':
            cart_item.quantity = max(1, cart_item.quantity - 1)
        
        cart_item.save()
    except CartItem.DoesNotExist:
        messages.error(request, 'Товар не найден в корзине')
    except Exception as e:
        messages.error(request, 'Ошибка при изменении количества')
    
    return redirect('cart')

def register(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Переносим корзину из сессии в корзину пользователя
            _migrate_session_cart_to_user_cart(user, request.session)
            messages.info(request, 'Товары из корзины перенесены в ваш профиль')
            
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Пытаемся найти пользователя по email, телефону или логину
            user = None
            try:
                # Сначала по email
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                try:
                    # Потом по телефону через профиль
                    profile = UserProfile.objects.get(phone=username)
                    user = profile.user
                except UserProfile.DoesNotExist:
                    # И наконец по имени пользователя (логину)
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        pass
            
            if user and user.check_password(password):
                login(request, user)
                
                # Переносим корзину из сессии в корзину пользователя
                _migrate_session_cart_to_user_cart(user, request.session)
                messages.info(request, 'Товары из корзины перенесены в ваш профиль')
                
                messages.success(request, f'Добро пожаловать, {user.first_name}!')
                return redirect('profile')
            else:
                messages.error(request, 'Неверный email/телефон или пароль')
    else:
        form = UserLoginForm()
    
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')

@login_required
def profile(request):
    """Личный кабинет пользователя"""
    # Получаем или создаем профиль пользователя
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'main/profile.html', {'form': form, 'profile': profile})

def contacts(request):
    return render(request, 'main/contacts.html')


@login_required
def cart(request):
    """Показать корзину пользователя"""
    cart = _get_or_create_cart(request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    
    items = []
    total = 0
    
    for cart_item in cart_items:
        line_total = cart_item.line_total
        total += line_total
        items.append({
            'product': cart_item.product,
            'qty': cart_item.quantity,
            'line_total': line_total,
        })
    
    return render(request, 'main/cart.html', {'items': items, 'total': total})

@login_required
def create_order(request):
    """Создать заказ из корзины"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Получаем корзину пользователя
            cart = _get_or_create_cart(request.user)
            cart_items = CartItem.objects.filter(cart=cart).select_related('product')
            
            if not cart_items.exists():
                messages.error(request, 'Корзина пуста')
                return redirect('cart')
            
            # Создаем заказ
            order = form.save(commit=False)
            order.user = request.user
            
            # Вычисляем общую сумму
            total_amount = sum(item.line_total for item in cart_items)
            order.total_amount = total_amount
            order.save()
            
            # Создаем элементы заказа
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Очищаем корзину
            cart_items.delete()
            
            messages.success(request, f'Заказ #{order.order_number} успешно оформлен! Мы свяжемся с вами в ближайшее время.')
            return redirect('cart')
    else:
        # Предзаполняем форму данными из профиля пользователя
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        initial_data = {
            'phone': profile.phone or '',
            'email': request.user.email or '',
            'address': profile.address or '',
            'city': profile.city or '',
            'postal_code': profile.postal_code or '',
        }
        form = OrderForm(initial=initial_data)
    
    return render(request, 'main/order_form.html', {'form': form})

