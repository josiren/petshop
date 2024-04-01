import random
from django.shortcuts import render, get_object_or_404
from petapp.models import Customer
from petapp.forms import *
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .authentication import EmailAuthBackend
from django.core.files.base import ContentFile
from django.db.models import Avg
from django.http import Http404, HttpResponse
from yookassa import Configuration, Payment


# Main navigation pages
def index(request):
    top_rated_products = Product.objects.annotate(avg_rating=Avg('rating__rating')).order_by('-avg_rating')[:3]
        
    return render(request, 'petapp/main.html', {'top_rated_products': top_rated_products})

def catalog(request):
    product_name = Product.objects.all()
    category = Product.objects.all()
    animal_type = Product.objects.all()
    rating = Rating.objects.all()

    if not Product.objects.exists(): 
        message = "Товаров временно нет"
        return render(request, 'petapp/catalog.html', {'message': message})

    return render(request, 'petapp/catalog.html', {'products': product_name, 'category' : category, 'animal_type' : animal_type, 'rating' : rating})

def contact(request):
    return render(request, 'petapp/contact.html')

def about(request):
    return render(request, 'petapp/about.html')


# Auth and Reg pages
def reg(request):
    if request.method == 'POST':
        auth_form = createUserForm(request.POST)
        reg_form = RegForm(request.POST)
        form = CombinedRegForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            phone = form.cleaned_data.get('phone')

            
            if not User.objects.filter(email=email).exists() and not Customer.objects.filter(phone=phone).exists():
                if 'last_name' in form.cleaned_data and 'first_name' in form.cleaned_data and 'patronymic' in form.cleaned_data:
                    if len(form.cleaned_data['last_name']) >= 2 and len(form.cleaned_data['first_name']) >= 2 and len(form.cleaned_data['patronymic']) >= 2:
                        auth_form.instance.username = f'{random.randrange(10000000)}'
                        user = auth_form.save()
                        user.set_password(user.password)
                        user = auth_form.save()
                        customer = reg_form.save(commit=False)
                        customer.user = user
                
                        try:
                            customer.save()
                            user = EmailAuthBackend().authenticate(request=request, email=email, password=password)
                            if user is not None:
                                login(request, user)
                                return redirect('home')

                        except IntegrityError:
                            form.add_error('phone', 'Пользователь с таким номером телефона уже существует.')
                    else:
                        form.add_error(None, 'Фамилия, имя и отчество должны содержать не менее 2 символов.')
                else:
                    form.add_error(None, 'Фамилия, имя и отчество являются обязательными полями.')
            else:
                form.add_error(None, 'Пользователь с такой электронной почтой или номером телефона уже существует.')
    
    else:
        form = CombinedRegForm()

    return render(request, 'petapp/reg.html', {'form': form})


def email_login(request):
    if request.user.is_authenticated:
        return redirect('user')
    
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = EmailAuthBackend().authenticate(request=request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Ошибка аутентификации")
    else:
        form = EmailLoginForm()
    return render(request, 'petapp/auth.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# Bakset page 
@login_required
def basket(request):
    customer = Customer.objects.get(user=request.user)
    if not Basket.objects.filter(user=customer).exists():
        basket = Basket.objects.create(user=customer)
    basket = Basket.objects.get(user=customer)
    basket_items = BasketProduct.objects.filter(basket=basket).order_by('product_id')
    basket_total = 0
    for a in basket_items:
        basket_total += int(a.quantity) * int(a.product.price)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = basket_total

            order_detail = OrderDetail.objects.create(
                amount=amount,
                basket=basket
            )
            order = Order.objects.create(
                user=customer,
                details=order_detail
            )
            return redirect('buy', order_num=order.id)
    else:
        form = PaymentForm()

    return render(request, 'petapp/basket.html', {"basket_items": basket_items, "basket_total": basket_total, "basket": basket, 'form': form})

@login_required
def add_basket(request, pk):
    customer = Customer.objects.get(user=request.user)
    if Basket.objects.filter(user=customer).exists():
        basket = Basket.objects.get(user=customer)
        product = get_object_or_404(Product, pk=pk)
        if BasketProduct.objects.filter(product=product, basket=basket).exists():
            basket_product = BasketProduct.objects.get(product=product, basket=basket)
            if int(basket_product.quantity) >= basket_product.product.stock:
                messages.error(request, "Ошибка, товаров на складе больше нет.")
            else:
                basket_items = BasketProduct.objects.filter(pk=basket_product.pk, basket=basket).update(quantity=int(basket_product.quantity) + 1)
        else:
            basket_items = BasketProduct.objects.create(product=product, basket=basket, quantity=1)
    else:
        basket = Basket.objects.create(user=customer)
        product = get_object_or_404(Product, pk=pk)
        basket_items = BasketProduct.objects.create(product=product, basket=basket, quantity=1)
    return redirect('catalog')


def addition_basket(request, product, basket):
    basket_product = BasketProduct.objects.get(pk=product)
    product = basket_product.product
    if int(basket_product.quantity) >= basket_product.product.stock:
        messages.error(request, "Ошибка, товаров на складе больше нет.")
    else:
        basket_items = BasketProduct.objects.filter(pk=basket_product.pk, basket=basket).update(quantity=int(basket_product.quantity) + 1)
    return redirect("basket")

def subtraction_basket(request, product, basket):
    basket_product = BasketProduct.objects.get(pk=product)
    if basket_product.quantity == 1:
        basket_product.delete()
    else:
        basket_items = BasketProduct.objects.filter(pk=product, basket_id=basket).update(quantity = int(basket_product.quantity) - 1)
    return redirect("basket")

#User page
def user(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        user = customer.user

    if not Basket.objects.filter(user=customer).exists():
        basket = Basket.objects.create(user=customer)
    basket = Basket.objects.get(user=customer)
    basket_items = BasketProduct.objects.filter(basket=basket).order_by('product_id')
    total_items = 0
    basket_total = 0
    for a in basket_items:
        basket_total += int(a.quantity) * int(a.product.price)
        total_items += a.quantity 
    return render(request, 'petapp/user.html', {'user': user, 'customer': customer,"basket_total": basket_total, 'total_items': total_items})

def user_edit(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        user = customer.user
    
    if request.method == 'POST':
        user.last_name = request.POST.get('surname')
        user.first_name = request.POST.get('name')
        user.email = request.POST.get('email')

        if User.objects.filter(email=user.email).exclude(pk=user.pk).exists():
            messages.error(request, "Пользователь с такой электронной почтой или номером телефона уже существует.")
            return render(request, 'petapp/user_edit.html', {'user': user, 'customer': customer})
        
        if Customer.objects.filter(phone=customer.phone).exclude(pk=customer.pk).exists():
            messages.error(request, "Phone number must be unique.")
            return render(request, 'petapp/user_edit.html', {'user': user, 'customer': customer})
        
        name_validator = RegexValidator(regex=r'^[a-zA-Zа-яА-Я]{2,}$', message="ФИО должно содержать только русские или английские буквы и быть длиной не менее 2 символов.")
        
        try:
            name_validator(user.last_name)
        except ValidationError as e:
            messages.error(request, e.message)
        
        try:
            name_validator(user.first_name)
        except ValidationError as e:
            messages.error(request, e.message)
        
        patronymic = request.POST.get('patronymic')
        if patronymic:
            try:
                name_validator(patronymic)
                customer.patronymic = patronymic
            except ValidationError as e:
                messages.error(request, e.message)
        
        phone = request.POST.get('phone')
        if phone:
            if Customer.objects.filter(phone=phone).exclude(pk=customer.pk).exists():
                messages.error(request, "Пользователь с таким номером телефона уже существует.")
                return render(request, 'petapp/user_edit.html', {'user': user, 'customer': customer})
            customer.phone = phone
        
        address = request.POST.get('address')
        if address:
            customer.address = address

        if 'photo_avatar' in request.FILES:
            photo = request.FILES['photo_avatar']
            if not photo.name.endswith(('.jpg', '.jpeg', '.png')):
                messages.error(request, "Допустимы только файлы формата JPG или PNG.") 

            else:
                if customer.photo_avatar:
                    old_photo_path = customer.photo_avatar.path
                    customer.photo_avatar.delete(save=False)

                new_photo_name = f"user_{user.id}_avatar"
                customer.photo_avatar.save(f"{new_photo_name}.jpg", ContentFile(photo.read()))

        if not messages.get_messages(request):
            user.save()
            customer.save()
            return redirect('user')

    return render(request, 'petapp/user_edit.html', {'user': user, 'customer': customer})


def buy_product(request, order_num):
    order = Order.objects.filter(id=order_num).first()
    if order and order.details:
        uuids = uuid.uuid4()
        payment = Payment.create({
            "amount": {
                "value": str(order.details.amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"http://127.0.0.1:8000/basket/buy/{order.id}/confirm-buy/"
            },
            "capture": True,
            "description": f"Заказ {order.id}"
        }, uuids)

        payment_id = payment.id
        order.details.payment_id = payment_id
        order.details.status = 'processing'
        order.details.save()

        return redirect(f'https://yoomoney.ru/checkout/payments/v2/contract?orderId={payment_id}')
    else:
        # Обработка случая, когда заказ не найден или не имеет деталей
        return HttpResponse("Заказ не найден или не имеет деталей")
    

def buy_confirm(request, pk):
    order = Order.objects.filter(order_number=pk).first()
    payment = Payment.find_one(OrderDetail.payment_id)
    
    if payment.description == f"Заказ {order.id}" and order.order_number == pk and request.user == order.user:
        if payment.status == "succeeded":
            error = False
            OrderDetail.status = 'paid'
            order.save()
            basket = get_object_or_404(Basket, user=request.user)
            basket_items = BasketProduct.objects.filter(basket=basket).order_by('product_id')
            
            for item in basket_items:
                product = Product.objects.get(pk=item.product.pk)
                if PurchaseHistory.objects.filter(order_number=order, product=product).exists():
                    break
                else:
                    PurchaseHistory.objects.create(order_number=order, user=request.user, product=product, quantity=item.quantity)
                    
                purchase = PurchaseHistory.objects.get(order_number=order, product=product)
                
                
                product_detail = Product.objects.filter(user__isnull=True, product=product)[:item.quantity]
                
                for pr_det in product_detail:
                    purchase.details.add(pr_det)
                    pr_det.user = request.user
                    pr_det.save()
                if product.stock - item.quantity == 0:
                    product.availability = True
                else:
                    product.stock = product.stock - item.quantity
                product.save()

            basket.delete()           
            return redirect('profile')
        else:
            error = True
            return render(request, 'petapp/confirm.html', {'basket_items': basket_items, 'error':error})
    raise Http404("Произошла ошибка" )

