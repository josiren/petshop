from django.shortcuts import render
from petapp.models import Customer
from petapp.forms import *
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password
import random

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
        form = CombinedForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')

            
            if not User.objects.filter(email=email).exists() and not Customer.objects.filter(phone=phone).exists():
                if 'last_name' in form.cleaned_data and 'first_name' in form.cleaned_data and 'patronymic' in form.cleaned_data:
                    if len(form.cleaned_data['last_name']) >= 2 and len(form.cleaned_data['first_name']) >= 2 and len(form.cleaned_data['patronymic']) >= 2:
                        auth_form.instance.username = f'{random.randrange(10000000)}'
                        user = auth_form.save()
                        customer = reg_form.save(commit=False)
                        customer.user = user
                
                        try:
                            customer.save()
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
        form = CombinedForm()

    return render(request, 'petapp/reg.html', {'form': form})


class LoginView(BaseLoginView):
    authentication_form = LoginUserForm
    template_name = "petapp/auth.html" 
    redirect_authenticated_user = True

def logout_view(request):
    logout(request)
    return redirect('home')

#  функцию для выхода пользователя из системы

login = LoginView.as_view()

# Bakset page 
def basket(request):
    return render (request, 'petapp/basket.html')

#User page
def user(request):
    return render(request, 'petapp/user.html')

def user_edit(request):
    return render(request, 'petapp/user_edit.html')