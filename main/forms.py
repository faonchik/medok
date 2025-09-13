from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, Order

class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        }),
        label='Email'
    )
    
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 999-99-99'
        }),
        label='Номер телефона (необязательно)'
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        }),
        label='Имя'
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию'
        }),
        label='Фамилия'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        label='Пароль'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        }),
        label='Подтверждение пароля'
    )
    
    class Meta:
        model = User
        fields = ('email', 'phone', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and UserProfile.objects.filter(phone=phone).exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone')
            )
        return user

class UserLoginForm(AuthenticationForm):
    """Форма входа пользователя"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email, телефон или логин'
        }),
        label='Email, телефон или логин'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        label='Пароль'
    )

class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = ('phone', 'middle_name', 'address', 'city', 'postal_code', 'birth_date')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        # Apply branded input styling
        self.fields['first_name'].widget.attrs.setdefault('class', 'form-control')
        self.fields['last_name'].widget.attrs.setdefault('class', 'form-control')
        self.fields['email'].widget.attrs.setdefault('class', 'form-control')
        self.fields['first_name'].widget.attrs.setdefault('placeholder', 'Имя')
        self.fields['last_name'].widget.attrs.setdefault('placeholder', 'Фамилия')
        self.fields['email'].widget.attrs.setdefault('placeholder', 'email@example.com')
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # Обновляем данные пользователя
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
        return profile

class OrderForm(forms.ModelForm):
    """Форма оформления заказа"""
    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 999-99-99',
            'pattern': r'^\+?1?\d{9,15}$'
        }),
        label='Телефон',
        help_text='Введите номер телефона для связи'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
        label='Email',
        help_text='Введите email для уведомлений о заказе'
    )
    
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Улица, дом, квартира',
            'rows': 3
        }),
        label='Адрес доставки',
        help_text='Укажите полный адрес доставки'
    )
    
    city = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Город'
        }),
        label='Город'
    )
    
    postal_code = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456',
            'pattern': r'^\d{6}$'
        }),
        label='Почтовый индекс',
        help_text='6 цифр'
    )
    
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Дополнительные пожелания к заказу',
            'rows': 3
        }),
        label='Комментарий к заказу',
        help_text='Необязательно'
    )
    
    class Meta:
        model = Order
        fields = ['phone', 'email', 'address', 'city', 'postal_code', 'comment']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Убираем все символы кроме цифр и +
            import re
            phone_clean = re.sub(r'[^\d+]', '', phone)
            if not re.match(r'^\+?1?\d{9,15}$', phone_clean):
                raise ValidationError('Введите корректный номер телефона')
            return phone_clean
        return phone
    
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            import re
            if not re.match(r'^\d{6}$', postal_code):
                raise ValidationError('Почтовый индекс должен содержать 6 цифр')
        return postal_code
