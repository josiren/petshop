import uuid
from PIL import Image
from django.db import models
from django.forms import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MaxValueValidator
from decimal import Decimal
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image, ImageDraw, ImageFont


def validate_image_size(image):
    max_width = 300
    max_height = 400
    img = Image.open(image)
    if img.width > max_width or img.height > max_height:
        raise ValidationError("Максимальные допустимые размеры изображения - 300x400 пикселей.")

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name = ("Пользователь"))
    patronymic = models.CharField(max_length=30, unique=False,verbose_name = ("Отчество"),  validators=[RegexValidator(r'^[a-zA-ZА-Яа-яЁё]+$', 'Разрешены только буквы.')])
    phone = PhoneNumberField(unique=True, blank=False, verbose_name = ("Номер телефона"))
    address = models.CharField(max_length=255, blank=True, verbose_name = ("Адрес"))
    photo_avatar = models.ImageField(upload_to='customer/', blank=True, null=True, verbose_name = ("Фото пользователь"))

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['user__date_joined']


    def save(self, *args, **kwargs):
        if not self.photo_avatar:
            initials = ''.join([name[0] for name in [self.user.last_name, self.user.first_name]]).upper()
            size = (110, 110)
            
            image = Image.new('RGB', size, '#F0F0F0') 
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("petapp\\static\\petapp\\GLOBAL\\fonts\\Gravity-Regular.ttf", 36)
            
            draw.text((36, 36), initials, fill='#949494', font=font)
            image.save(f'media/customer/{self.user.username}_avatar.jpg')

            self.photo_avatar.name = f'customer/{self.user.username}_avatar.jpg'

        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.customer.save()


class Animal_type(models.Model):
    name = models.CharField(max_length=255, verbose_name = ("Название"), validators=[RegexValidator(r'^[a-zA-ZА-Яа-яЁё]+$', 'Разрешены только буквы.')], unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип животного"
        verbose_name_plural = "Типы животных"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name = ("Название"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
  

class Product(models.Model):
    product_name = models.CharField(max_length=255, unique=True, verbose_name = ("Название продукта"),)
    price = models.PositiveIntegerField(default=0, verbose_name = ("Цена"))
    description = models.TextField(verbose_name = ("Описание"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name = ("Категория"))
    manufacturer = models.CharField(max_length=100, verbose_name = ("Производитель"))
    origin_country = models.CharField(max_length=100, verbose_name = ("Страна производитель"))
    photo_product = models.ImageField(upload_to='products/', validators=[validate_image_size], verbose_name = ("Фото продукта"))
    animal_type = models.ManyToManyField(Animal_type, related_name='products', verbose_name = ("Тип животного"))
    weight = models.DecimalField(default=Decimal('0.0'), max_digits=10, decimal_places=2, verbose_name = ("Вес"))
    availability = models.BooleanField(verbose_name = ("Наличие"))
    stock = models.PositiveIntegerField(default=0, verbose_name = ("Склад"))
    
    def save(self, *args, **kwargs):
        if self.stock > 0:
            self.availability = True  
        else:
            self.availability = False  
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
            return f"{self.product_name} - {self.price} р"
    
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['-rating']


class Basket(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name = ("Пользователь"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name = ("Дата создания"))
    
    def __str__(self):
        return f"Корзина: {self.user}"
    
    class Meta:
        verbose_name = ("Корзину")
        verbose_name_plural = ("Корзины")


class BasketProduct(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, verbose_name = ("Корзина пользователя"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name = ("Продукт"))
    quantity = models.PositiveIntegerField(verbose_name = ("Количество"))

    def __str__(self):
        return f"{self.basket}: {self.product} - {self.quantity}"
    
    class Meta:
        verbose_name = "Корзина продуктов"
        verbose_name_plural = "Корзины продуктов"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name = ("Пользователь"))
    order_date = models.DateField(verbose_name = ("Дата заказа"))
    shipping_address = models.TextField(verbose_name = ("Адрес доставки"))

    def __str__(self):
        return f"Заказ {self.id} от {self.customer}"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-order_date']


class OrderDetail(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('error', 'Error'),
    ]

    order_number = models.UUIDField(default = uuid.uuid4, verbose_name = ("Номер заказа"))
    order = models.OneToOneField(Order, related_name='details', on_delete=models.CASCADE, verbose_name = ("Заказ"))
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, verbose_name = ("Корзина"))
    payment_id = models.CharField(max_length=128, blank=True, verbose_name = ("Идентификатор платежа"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name = ("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name = ("Обновлённая дата ")) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name = ("Статус"))

    def __str__(self):
        return f"Деталь {self.id} из заказа {self.order_id}"
    
    class Meta:
        verbose_name = "Детали заказа"
        verbose_name_plural = "Детали заказов"
        ordering = ['-order']


class PurchaseHistory(models.Model):  
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name = ("Пользователь"))
    order_number = models.ForeignKey(OrderDetail, on_delete=models.CASCADE, verbose_name = ("Номер заказа"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name = ("Дата создания"))
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, verbose_name = ("Корзина"))

    class Meta:
        verbose_name = "История покупок"
        verbose_name_plural = "История покупки"


class Rating(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name = ("Пользователь"))
    purchase_history = models.OneToOneField(PurchaseHistory, on_delete=models.CASCADE, primary_key=True, verbose_name = ("История покупок"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name = ("Продукт"))
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)], default=0, verbose_name = ("Рейтинг"))

    class Meta:
        verbose_name = "Рейтинги"
        verbose_name_plural = "Рейтинг"
