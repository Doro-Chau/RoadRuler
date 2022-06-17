from django.urls import path, include
from . import views
from .views import hello, verify_domain

urlpatterns = [
    path('hello/<name>', hello),
    path('.well-known/pki-validation/<file>', verify_domain)
]
