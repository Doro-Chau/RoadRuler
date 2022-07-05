from django.urls import path, include
from . import views

urlpatterns = [
    path('getData', views.getData),
    path('map', views.map),
    path('renderCctv', views.renderCctv),
    path('renderLivevd', views.renderLivevd),
    path('renderLivecity', views.renderLivecity),
    path('renderAlert', views.renderAlert),
    path('renderParking', views.renderParking),
    path('renderConstruction', views.renderConstruction)
]
