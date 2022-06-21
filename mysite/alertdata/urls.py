from django.urls import path, include
from . import views
from .views import getData, verify_domain

urlpatterns = [
    path('.well-known/pki-validation/<file>', verify_domain),
    path('getData', getData),
    path('map', views.map)
]
