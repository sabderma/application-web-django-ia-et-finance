from rest_framework import serializers
from .models import Category, Expense, RecurringExpense


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "active"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Category.objects.create(user=user, **validated_data)


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
        return category

    def create(self, validated_data):
        user = self.context["request"].user
        return Expense.objects.create(user=user, **validated_data)


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
        return category

    def validate_day_of_month(self, v):
        if v < 1 or v > 31:
            raise serializers.ValidationError("day_of_month doit être entre 1 et 31.")
        return v

    def create(self, validated_data):
        user = self.context["request"].user
        return RecurringExpense.objects.create(user=user, **validated_data)



#----------------
from decimal import Decimal, ROUND_CEILING
from datetime import date

from django.utils import timezone
from rest_framework import serializers

from .models import PurchaseSimulation, Expense, RecurringExpense


class PurchaseSimulateInputSerializer(serializers.Serializer):
    item_name = serializers.CharField(max_length=120)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    priority = serializers.ChoiceField(choices=["NEED", "WANT", "LUXURY"], default="WANT")
    desired_date = serializers.DateField(required=False, allow_null=True)

    # option: l'utilisateur impose combien il veut mettre de côté par mois
    monthly_saving_target = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True
    )


class PurchaseSimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSimulation
        fields = "__all__"
        read_only_fields = ["id", "user", "decision", "estimated_months", "recommended_monthly_saving", "details", "created_at"]
