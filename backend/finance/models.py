from django.conf import settings
from django.db import models

from django.utils import timezone

from django.core.validators import MinValueValidator, MaxValueValidator

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
    class Statut(models.TextChoices):
        ETUDIANT = "ETUDIANT", "Étudiant"
        SALARIE = "SALARIE", "Salarié"
        RETRAITE = "RETRAITE", "Retraité"

    # ... tes champs existants
    age = models.PositiveIntegerField(
    default=18,
    validators=[MinValueValidator(16), MaxValueValidator(100)]
    )

    statut = models.CharField(
    max_length=10,
    choices=Statut.choices,
    default=Statut.ETUDIANT
    )


    def __str__(self):
        return f"Profil financier de {self.user.username}"


from django.conf import settings
from django.db import models


class Category(models.Model):
    class CategoryType(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        SUBSCRIPTION = "SUBSCRIPTION", "Abonnement"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    name = models.CharField(max_length=80)

    # ✅ On garde uniquement le type
    type = models.CharField(
        max_length=20,
        choices=CategoryType.choices,
        default=CategoryType.NORMAL,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "type"],
                name="uniq_category_per_user_name_type"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.type})"
    


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    category = models.ForeignKey(
    Category,
    on_delete=models.CASCADE,   
    related_name="expenses",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.amount}"


class RecurringExpense(models.Model):
   
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurring_expenses",
    )
    category = models.ForeignKey(
    Category,
    on_delete=models.CASCADE,   
    related_name="recurring_expenses",
    )

    name = models.CharField(max_length=120)  # ex: Netflix
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # optionnel
    day_of_month = models.PositiveSmallIntegerField(default=1)  

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
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.WANT
    )

    # ✅ supprimé : desired_date

    decision = models.CharField(max_length=15, choices=Decision.choices)
    estimated_months = models.PositiveIntegerField(default=0)
    recommended_monthly_saving = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item_name} - {self.decision}"
