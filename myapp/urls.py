from django.urls import path
from . import views
from myapp.views import run_migrations 
urlpatterns = [
    
    path('', views.predict, name='home'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/general-test/submit/', views.submit_general_test),
    path('api/general-test/results/', views.test_results),
    path('api/general-test/results/<int:result_id>/', views.test_result_detail),
    path('run-migrations/', run_migrations),
]
