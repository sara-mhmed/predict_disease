from django.urls import path
from .views import GeneralTestApiView, TestResultsApiView

urlpatterns = [
    path("predict/", GeneralTestApiView.as_view(), name="api_predict"),
    path("results/", TestResultsApiView.as_view(), name="api_results"),
]
