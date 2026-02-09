from django.conf import settings
from django.db import models

from django.utils import timezone

class FinancialProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="financial_profile",
    )
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    salaire_mensuel = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    depenses_fixes = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=True,
    blank=True,
    default=0)

    objectif_epargne = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Profil financier de {self.user.username}"


class Category(models.Model):
    # Catégorie propre à l'utilisateur
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=80)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="uniq_category_per_user")
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.amount}"


class RecurringExpense(models.Model):
    """
    Abonnement / dépense récurrente (ex: Netflix 20€ le 2 de chaque mois)
    On l'utilise pour calculer les totaux mensuels sans créer 100 lignes Expense.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurring_expenses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="recurring_expenses",
    )

    name = models.CharField(max_length=120)  # ex: Netflix
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # optionnel
    day_of_month = models.PositiveSmallIntegerField(default=1)  # 1..28/31

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.amount}€)"


#-----------


class PurchaseSimulation(models.Model):
    class Priority(models.TextChoices):
        NEED = "NEED", "Besoin"
        WANT = "WANT", "Envie"
        LUXURY = "LUXURY", "Luxe"

    class Decision(models.TextChoices):
        BUY_NOW = "BUY_NOW", "Acheter maintenant"
        WAIT = "WAIT", "Attendre"
        NOT_POSSIBLE = "NOT_POSSIBLE", "Non possible"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchase_simulations",
    )

    item_name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.WANT)

    desired_date = models.DateField(null=True, blank=True)

    decision = models.CharField(max_length=15, choices=Decision.choices)
    estimated_months = models.PositiveIntegerField(default=0)
    recommended_monthly_saving = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    details = models.JSONField(default=dict, blank=True)  # totals, warnings, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item_name} - {self.decision}"
