from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from decimal import Decimal

class UserProfile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр."
    )
    
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Номер телефона"
    )
    
    # Дополнительные поля
    middle_name = models.CharField(max_length=30, verbose_name="Отчество", blank=True)
    
    # Адрес
    address = models.TextField(verbose_name="Адрес", blank=True)
    city = models.CharField(max_length=100, verbose_name="Город", blank=True)
    postal_code = models.CharField(max_length=10, verbose_name="Почтовый индекс", blank=True)
    
    # Дополнительная информация
    birth_date = models.DateField(verbose_name="Дата рождения", blank=True, null=True)
    is_verified = models.BooleanField(default=False, verbose_name="Подтвержденный пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"Профиль {self.user.username}"

class HoneyProduct(models.Model):
    # Основная информация
    title = models.CharField(max_length=200, verbose_name="Название продукта")
    short_description = models.CharField(
        max_length=300,
        verbose_name="Краткое описание",
        help_text="Короткое описание под названием (например: 'Натуральный мед высшего качества')"
    )

    # Детали продукта
    detailed_description = models.TextField(
        verbose_name="Подробное описание",
        help_text="Полное описание продукта с деталями"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        help_text="Цена в рублях"
    )
    weight = models.CharField(
        max_length=50,
        verbose_name="Вес",
        default="1000P",
        help_text="Например: 500г, 1кг, 1000P"
    )

    # Изображение
    image = models.ImageField(
        upload_to='honey_products/',
        verbose_name="Изображение продукта",
        help_text="Рекомендуемый размер: 369x365px для карточки товара"
    )

    # Статус
    is_active = models.BooleanField(default=True, verbose_name="Активный товар")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый товар")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Медовая продукция"
        verbose_name_plural = "Медовая продукция"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.weight}"

class WaxCandle(models.Model):
    # Основная информация
    title = models.CharField(max_length=200, verbose_name="Название свечи")
    short_description = models.CharField(
        max_length=300,
        verbose_name="Краткое описание",
        help_text="Короткое описание под названием (например: 'Натуральная восковая свеча')"
    )

    # Детали продукта
    detailed_description = models.TextField(
        verbose_name="Подробное описание",
        help_text="Полное описание свечи с деталями"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        help_text="Цена в рублях"
    )
    weight = models.CharField(
        max_length=50,
        verbose_name="Вес",
        default="100г",
        help_text="Например: 50г, 100г, 200г"
    )

    # Изображение
    image = models.ImageField(
        upload_to='wax_candles/',
        verbose_name="Изображение свечи",
        help_text="Рекомендуемый размер: 369x365px для карточки товара"
    )

    # Статус
    is_active = models.BooleanField(default=True, verbose_name="Активная свеча")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемая свеча")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Восковая свеча"
        verbose_name_plural = "Восковые свечи"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.weight}"

class Cart(models.Model):
    """Корзина пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user.username}"

class CartItem(models.Model):
    """Элемент корзины"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Корзина")
    product = models.ForeignKey(HoneyProduct, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        unique_together = ['cart', 'product']  # Один товар может быть в корзине только один раз

    def __str__(self):
        return f"{self.product.title} x{self.quantity} в корзине {self.cart.user.username}"

    @property
    def line_total(self):
        """Общая стоимость элемента корзины"""
        return self.quantity * self.product.price

class Order(models.Model):
    """Заказ пользователя"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Номер заказа")
    
    # Контактная информация
    phone = models.CharField(max_length=17, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    
    # Адрес доставки
    address = models.TextField(verbose_name="Адрес доставки")
    city = models.CharField(max_length=100, verbose_name="Город")
    postal_code = models.CharField(max_length=10, verbose_name="Почтовый индекс")
    
    # Дополнительная информация
    comment = models.TextField(blank=True, verbose_name="Комментарий к заказу")
    
    # Статус и даты
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name="Статус заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    # Стоимость
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.order_number} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """Элемент заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(HoneyProduct, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")
    
    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
    
    def __str__(self):
        return f"{self.product.title} x{self.quantity} в заказе {self.order.order_number}"
    
    @property
    def line_total(self):
        """Общая стоимость элемента заказа"""
        return self.quantity * self.price