"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from petapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
<<<<<<< HEAD
    path('auth/', views.email_login, name='auth'),
    path('logout/', views.logout_view, name='logout'),
=======
    path('auth/', views.auth, name='auth'),
>>>>>>> master
    path('reg/', views.reg, name='reg'),
    path('basket/', views.basket, name='basket'),
    path('user/', views.user, name='user'),
    path('user/edit/', views.user_edit, name='user_edit'),
<<<<<<< HEAD
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
]
>>>>>>> master
