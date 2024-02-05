from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'petapp/main.html')

def contact(request):
    return render(request, 'petapp/contact.html')