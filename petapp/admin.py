from django.contrib import admin
from .models import Basket, Customer, Product, Animal_type, Category, Order, OrderDetail, PurchaseHistory, Rating, BasketProduct
from django.utils.safestring import mark_safe


admin.site.site_header = "Страница администратора"
admin.site.site_title = "Зоомагазин puffball"
admin.site.index_title = "Администрирование сайта"


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_last_name', 'get_first_name', 'phone', 'get_email', 'avatar_show')

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Фамилия'

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'Имя'

    def get_email(self, obj):
        return obj.user.email
    get_first_name.short_description = 'Электронная почта'

    def avatar_show(self, obj):
        if obj.photo_avatar:
            return mark_safe("<img src='{}' width='60' />".format(obj.photo_avatar.url))
        return "None"

    avatar_show.__name__ = "Картинка"


class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_name", "price", "availability", "stock", "image_show")
    readonly_fields = ['availability']

    def image_show(self, obj):
        if obj.photo_product:
            return mark_safe("<img src='{}' width='60' />".format(obj.photo_product.url))
        return "None"

    image_show.__name__ = "Картинка"


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Animal_type)
admin.site.register(Category)
admin.site.register(Basket)
admin.site.register(BasketProduct)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(PurchaseHistory)
admin.site.register(Rating)