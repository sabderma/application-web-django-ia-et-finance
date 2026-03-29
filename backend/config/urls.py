from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include



urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth
    path("api/auth/login/", TokenObtainPairView.as_view(), name="jwt_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("api/", include("accounts.urls")),

    # Finance API
    path("api/", include("finance.urls")),

    path("api/ml/", include("mlapp.urls")),

 

]
    