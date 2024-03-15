"""
URL configuration for rinha_de_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path

from pessoas import views


urlpatterns = [
    path("pessoas", views.PessoaView.as_view(), name="pessoas"),
    path("pessoas/<uuid:pessoa_pk>", views.PessoaView.as_view(), name="pessoa"),
    path("contagem-pessoas", views.contagem_pessoas, name="contagem-pessoas"),
    path("gevent-loop", views.gevent_loop, name="gevent-loop"),

    # path('admin/', admin.site.urls),
]
