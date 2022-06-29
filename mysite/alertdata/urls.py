from django.urls import path, include
from . import views
from .views import getData, getParking, verify_domain

urlpatterns = [
    path('.well-known/pki-validation/<file>', verify_domain),
    path('getData', getData),
    path('map', views.map),
    path('getTraffic', views.getTraffic),
    path('getCCTV', views.getCCTV),
    path('getSection', views.getSection),
    path('getLink', views.getLink),
    path('getLive', views.getLive),
    path('renderCctv', views.renderCctv),
    path('renderLivevd', views.renderLivevd),
    path('renderLivecity', views.renderLivecity),
    path('renderAlert', views.renderAlert),
    path('getParking', views.getParking),
    path('renderParking', views.renderParking)
]
