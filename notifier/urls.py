from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('deploy/', views.trigger_deploy, name='trigger_deploy'),
    path('webhook/', views.webhook_handler, name='webhook_handler'),
]
