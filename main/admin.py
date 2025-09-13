from django.contrib import admin
from django.utils.html import format_html
from .models import HoneyProduct, WaxCandle, UserProfile, Cart, CartItem, Order, OrderItem

@admin.register(HoneyProduct)
class HoneyProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'weight', 'is_active', 'is_featured', 'image_preview']
    list_filter = ['is_active', 'is_featured', 'created_at']
    search_fields = ['title', 'short_description']
    list_editable = ['is_active', 'is_featured']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'short_description', 'detailed_description')
        }),
        ('Цена и вес', {
            'fields': ('price', 'weight')
        }),
        ('Изображение', {
            'fields': ('image', 'image_display')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_featured')
        }),
    )

    readonly_fields = ['image_display']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "—"
    image_preview.short_description = 'Изображение'

    def image_display(self, obj):
        if obj.image:
            return format_html(
                '<div style="border: 2px solid #f0f0f0; border-radius: 12px; padding: 10px; display: inline-block;">'
                '<img src="{}" width="369" height="365" style="object-fit: cover; border-radius: 8px;" />'
                '<p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">Размер карточки: 450x468px</p>'
                '<p style="margin: 0; font-size: 12px; color: #666;">Изображение: 369x365px</p>'
                '</div>',
                obj.image.url
            )
        return "Изображение не загружено"
    image_display.short_description = 'Предпросмотр карточки'

@admin.register(WaxCandle)
class WaxCandleAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'weight', 'is_active', 'is_featured', 'image_preview']
    list_filter = ['is_active', 'is_featured', 'created_at']
    search_fields = ['title', 'short_description']
    list_editable = ['is_active', 'is_featured']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'short_description', 'detailed_description')
        }),
        ('Цена и вес', {
            'fields': ('price', 'weight')
        }),
        ('Изображение', {
            'fields': ('image', 'image_display')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_featured')
        }),
    )

    readonly_fields = ['image_display']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "—"
    image_preview.short_description = 'Изображение'

    def image_display(self, obj):
        if obj.image:
            return format_html(
                '<div style="border: 2px solid #f0f0f0; border-radius: 12px; padding: 10px; display: inline-block;">'
                '<img src="{}" width="369" height="365" style="object-fit: cover; border-radius: 8px;" />'
                '<p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">Размер карточки: 450x468px</p>'
                '<p style="margin: 0; font-size: 12px; color: #666;">Изображение: 369x365px</p>'
                '</div>',
                obj.image.url
            )
        return "Изображение не загружено"
    image_display.short_description = 'Предпросмотр карточки'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at', 'city']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Контактная информация', {
            'fields': ('phone', 'middle_name', 'birth_date')
        }),
        ('Адрес', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('Статус', {
            'fields': ('is_verified', 'created_at')
        }),
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'line_total']
    search_fields = ['cart__user__username', 'product__title']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'email')
        }),
        ('Адрес доставки', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'line_total']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__title']