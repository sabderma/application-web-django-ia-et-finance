from django.contrib import admin
from .models import (
    FinancialProfile,
    Category,
    Expense,
    RecurringExpense,
    PurchaseSimulation,
)


@admin.register(FinancialProfile)
class FinancialProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "solde", "salaire_mensuel", "depenses_fixes", "objectif_epargne")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # ✅ active supprimé du modèle Category
    list_display = ("user", "name", "type")
    list_filter = ("type",)
    search_fields = ("user__username", "name")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "amount", "date")
    list_filter = ("category", "date")
    search_fields = ("user__username", "description")


@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    # ✅ ici active existe toujours (RecurringExpense.active)
    list_display = ("user", "name", "amount", "day_of_month", "start_date", "end_date", "active")
    list_filter = ("active", "day_of_month")
    search_fields = ("user__username", "name")


@admin.register(PurchaseSimulation)
class PurchaseSimulationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item_name", "price", "decision", "estimated_months", "created_at")
    list_filter = ("decision", "priority", "created_at")
    search_fields = ("item_name", "user__username")