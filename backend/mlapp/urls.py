from django.urls import path
from .views import MLPredictFromProfileView

urlpatterns = [
    path("predict/", MLPredictFromProfileView.as_view()),
]
