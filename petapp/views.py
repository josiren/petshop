import os
import random
from django.shortcuts import render
from petapp.models import Customer
from petapp.forms import *
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .authentication import EmailAuthBackend
from django.core.files.images import get_image_dimensions
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile


# Main navigation pages
def index(request):
    return render(request, 'petapp/main.html')

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
def basket(request):
    return render (request, 'petapp/basket.html')

#User page
def user(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        user = customer.user
    return render(request, 'petapp/user.html', {'user': user, 'customer': customer})

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
        
        # Validate patronymic if not empty
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
            photo_avatar = request.FILES['photo_avatar']
            
            upload_path = customer.photo_avatar.field.upload_to
            file_name = photo_avatar.name
            file_path = os.path.join(upload_path, file_name)

            with Image.open(photo_avatar) as image:
                image.save(file_path, 'JPEG')
                image.save(file_path.replace('.jpg', '.png'), 'PNG')
            
            if customer.photo_avatar:
                customer.photo_avatar.delete()
            
            customer.photo_avatar.save(photo_avatar.name, ContentFile(photo_avatar.read()))
            customer.save()

        if not messages.get_messages(request):
            user.save()
            customer.save()
            return redirect('user')

    return render(request, 'petapp/user_edit.html', {'user': user, 'customer': customer})
