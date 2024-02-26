from django.shortcuts import render

# Create your views here.

# Main navigation pages
def index(request):
    return render(request, 'petapp/main.html')

def catalog(request):
    return render(request, 'petapp/catalog.html')

def contact(request):
    return render(request, 'petapp/contact.html')

def about(request):
    return render(request, 'petapp/about.html')


# Auth and Reg pages
def auth(request):
    return render(request, 'petapp/auth.html')

def reg(request):
    return render(request, 'petapp/reg.html')

# Bakset page 
def basket(request):
    return render (request, 'petapp/basket.html')

#User page
def user(request):
    return render(request, 'petapp/user.html')