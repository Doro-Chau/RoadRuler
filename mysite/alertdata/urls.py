from django.urls import path, include
from . import views
from .views import hello

urlpatterns = [
    path('hello/<name>', hello)
]
