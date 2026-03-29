from rest_framework import serializers
from .models import (
    Category,
    Expense,
    RecurringExpense,
    FinancialProfile,
    PurchaseSimulation,
)

# --------------------
# CATEGORY
# --------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Category.objects.create(user=user, **validated_data)
    
# --------------------
# EXPENSE
# --------------------

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Expense
        fields = ["id", "category", "category_name", "amount", "date", "description"]
        read_only_fields = ["id", "category_name"]

    def validate_category(self, category):
        user = self.context["request"].user

        if category.user_id != user.id:
            raise serializers.ValidationError("Cette catégorie ne t'appartient pas.")

        if category.type != "NORMAL":
            raise serializers.ValidationError(
                "Une dépense normale doit utiliser une catégorie de type NORMAL."
            )

        return category

    def create(self, validated_data):
        user = self.context["request"].user
        return Expense.objects.create(user=user, **validated_data)

# --------------------
# RECURRING EXPENSE
# --------------------
class RecurringExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = RecurringExpense
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "amount",
            "start_date",
            "end_date",
            "day_of_month",
            "active",
        ]
        read_only_fields = ["id", "category_name"]

    def validate_category(self, category):
        user = self.context["request"].user

        if category.user_id != user.id:
            raise serializers.ValidationError("Cette catégorie ne t'appartient pas.")

        if category.type != "SUBSCRIPTION":
            raise serializers.ValidationError(
                "Un abonnement doit utiliser une catégorie de type SUBSCRIPTION."
            )

        return category

    def create(self, validated_data):
        user = self.context["request"].user
        return RecurringExpense.objects.create(user=user, **validated_data)

# --------------------
# FINANCIAL PROFILE
# --------------------

class FinancialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialProfile
        fields = [
            "id",
            "solde",
            "salaire_mensuel",
            "depenses_fixes",
            "objectif_epargne",
            "age",
            "statut",
        ]
        read_only_fields = ["id"]

    def validate_age(self, v):
        if v < 16 or v > 100:
            raise serializers.ValidationError("L'âge doit être entre 16 et 100.")
        return v


# --------------------
# PURCHASE SIMULATION (INPUT + OUTPUT)
# --------------------

class PurchaseSimulateInputSerializer(serializers.Serializer):
    item_name = serializers.CharField(max_length=120)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    priority = serializers.ChoiceField(
        choices=["NEED", "WANT", "LUXURY"],
        default="WANT"
    )
    monthly_saving_target = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True
    )


class PurchaseSimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSimulation
        fields = [
            "id",
            "item_name",
            "price",
            "priority",
            "decision",
            "estimated_months",
            "recommended_monthly_saving",
            "details",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "decision",
            "estimated_months",
            "recommended_monthly_saving",
            "details",
            "created_at",
        ]







class AdviceInputSerializer(serializers.Serializer):
    simulation_id = serializers.IntegerField()