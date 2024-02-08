from django.shortcuts import render

# Create your views here.

# Main navigation pages
def index(request):
    context = {
        "home_page": "active-under" if request.resolver_match.url_name == "home" else ""
    }
    return render(request, 'petapp/main.html', context)


def catalog(request):
    context = {
        "catalog_page": "active-under" if request.resolver_match.url_name == "catalog" else ""
    }
    return render(request, 'petapp/catalog.html', context)

def contact(request):
    context = {
        "contact_page": "active-under" if request.resolver_match.url_name == "contact" else ""
    }
    return render(request, 'petapp/contact.html', context)

def about(request):
    context = {
        "about_page": "active-under" if request.resolver_match.url_name == "about" else ""
    }
    return render(request, 'petapp/about.html', context)


# Auth and Reg pages
def auth(request):
    context = {
        "auth_page": "active-color-swap" if request.resolver_match.url_name == "auth" else ""
    }
    return render(request, 'petapp/auth.html', context)

def reg(request):
    context = {
        "reg_page": "active-color-swap" if request.resolver_match.url_name == "reg" else ""
    }
    return render(request, 'petapp/reg.html', context)

#Order pages
def basket(request):
    context = {
        "basket_page": "active-color-swap" if request.resolver_match.url_name == "basket" else ""
    }
    return render (request, 'petapp/basket.html', context)
