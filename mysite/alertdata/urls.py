from django.urls import path, include
from . import views

urlpatterns = [
    path('.well-known/pki-validation/<file>', views.verify_domain),
    path('getData', views.getData),
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
