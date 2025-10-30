from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.predict, name='home'),
    path('api/predict/', views.api_predict, name='api_predict'),
   path('checktables/', views.list_tables, name='checktables'),


]
