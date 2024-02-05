from django.shortcuts import render

# Create your views here.
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

