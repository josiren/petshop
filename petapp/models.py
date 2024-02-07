from django.db import models

class Client(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    registration_date = models.DateField()
    photo_avatar = models.BinaryField()

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
    

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    origin_country = models.CharField(max_length=100)
    photo_product = models.BinaryField()
    animal_type = models.CharField(max_length=100)
    weight = models.FloatField()
    rating = models.IntegerField()

    def __str__(self):
        return self.name


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sale_date = models.DateField()
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class Warehouse(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    availability = models.BooleanField()
    quantity = models.IntegerField()