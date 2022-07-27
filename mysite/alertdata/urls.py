from django.urls import path, include
from . import views

urlpatterns = [
    path('get_data', views.get_data),
    path('', views.map),
    path('render_cctv', views.render_cctv),
    path('render_livevd', views.render_livevd),
    path('render_livecity', views.render_livecity),
    path('render_alert', views.render_alert),
    path('render_parking', views.render_parking),
    path('render_construction', views.render_construction),
    path('maplot', views.maplot),
    path('monitor', views.monitor),
    path('monitor_alert', views.monitor_alert),
    path('monitor_realtime', views.monitor_realtime),
    path('monitor_daily', views.monitor_daily)
]
