from django.urls import path
from .views import (
    CategoryListCreateView,
    ExpenseListCreateView,
    ExpenseDetailView,
    RecurringExpenseListCreateView,
    RecurringExpenseDetailView,
)
from .views import PurchaseSimulateView
from .views import DashboardView
from .views import PurchaseSimulationListView, PurchaseSimulationDetailView


urlpatterns = [
    path("categories/", CategoryListCreateView.as_view()),
    path("expenses/", ExpenseListCreateView.as_view()),
    path("expenses/<int:pk>/", ExpenseDetailView.as_view()),

    path("recurring-expenses/", RecurringExpenseListCreateView.as_view()),
    path("recurring-expenses/<int:pk>/", RecurringExpenseDetailView.as_view()),

    path("simulate/", PurchaseSimulateView.as_view()),

    path("dashboard/", DashboardView.as_view()),

    path("simulations/", PurchaseSimulationListView.as_view()),
    path("simulations/<int:pk>/", PurchaseSimulationDetailView.as_view()),



]
