from django.urls import path
from .views import general_test_view

urlpatterns = [
    path('', general_test_view, name='general_test_page'),
]
