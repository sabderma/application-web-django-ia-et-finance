from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,

    ExpenseListCreateView,
    ExpenseDetailView,

    RecurringExpenseListCreateView,
    RecurringExpenseDetailView,

    PurchaseSimulateView,
    PurchaseSimulationListView,
    PurchaseSimulationDetailView,

    DashboardView,
    FinancialProfileMeView,
    CategoryAllListView,
    AdviceView,
)


urlpatterns = [

    # --------------------
    # CATEGORIES
    # --------------------
    path("categories/", CategoryListCreateView.as_view(), name="categories-list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="categories-detail"),
    path("categories/all/", CategoryAllListView.as_view(), name="categories-all"),


    # --------------------
    # EXPENSES
    # --------------------
    path("expenses/", ExpenseListCreateView.as_view(), name="expenses-list"),
    path("expenses/<int:pk>/", ExpenseDetailView.as_view(), name="expenses-detail"),

    # --------------------
    # RECURRING EXPENSES
    # --------------------
    path("recurring-expenses/", RecurringExpenseListCreateView.as_view(), name="recurring-list"),
    path("recurring-expenses/<int:pk>/", RecurringExpenseDetailView.as_view(), name="recurring-detail"),

    # --------------------
    # PURCHASE SIMULATION
    # --------------------
    path("simulate/", PurchaseSimulateView.as_view(), name="simulate"),
    path("simulations/", PurchaseSimulationListView.as_view(), name="simulations-list"),
    path("simulations/<int:pk>/", PurchaseSimulationDetailView.as_view(), name="simulations-detail"),

    # --------------------
    # DASHBOARD
    # --------------------
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    # --------------------
    # FINANCIAL PROFILE
    # --------------------
    path("financial-profile/me/", FinancialProfileMeView.as_view(), name="financial-profile"),

    path("advice/", AdviceView.as_view(), name="advice"),
]
