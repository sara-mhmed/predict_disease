from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.predict, name='home'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/general-test/submit/', views.submit_general_test),








]
