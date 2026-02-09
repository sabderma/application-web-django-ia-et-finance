from rest_framework import generics, permissions
from .models import Category, Expense, RecurringExpense
from .serializers import (
    CategorySerializer,
    ExpenseSerializer,
    RecurringExpenseSerializer,
)
from decimal import Decimal, ROUND_CEILING
from datetime import date

from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user, active=True).order_by("name")


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).order_by("-date")


class ExpenseDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


class RecurringExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = RecurringExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecurringExpense.objects.filter(user=self.request.user).order_by("-created_at")


class RecurringExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecurringExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecurringExpense.objects.filter(user=self.request.user)
    


#----------historique

from .models import PurchaseSimulation
from .serializers import PurchaseSimulationSerializer


class PurchaseSimulationListView(generics.ListAPIView):
    serializer_class = PurchaseSimulationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseSimulation.objects.filter(user=self.request.user).order_by("-created_at")


class PurchaseSimulationDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = PurchaseSimulationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseSimulation.objects.filter(user=self.request.user)




#----------------------



def _month_bounds(d: date):
    first = d.replace(day=1)
    if first.month == 12:
        next_first = first.replace(year=first.year + 1, month=1)
    else:
        next_first = first.replace(month=first.month + 1)
    return first, next_first


def _ceil_div(a: Decimal, b: Decimal) -> int:
    if b <= 0:
        return 0
    return int((a / b).to_integral_value(rounding=ROUND_CEILING))


class PurchaseSimulateView(APIView):
    """
    POST /api/simulate/
    Calcule: acheter maintenant ou attendre
    """
    def post(self, request):
        from .models import FinancialProfile, Expense, RecurringExpense, PurchaseSimulation
        from .serializers import PurchaseSimulateInputSerializer, PurchaseSimulationSerializer

        inp = PurchaseSimulateInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        data = inp.validated_data

        user = request.user
        item_name = data["item_name"]
        price: Decimal = data["price"]
        priority = data["priority"]
        desired_date = data.get("desired_date")
        monthly_target = data.get("monthly_saving_target")

        # 1) Profil financier
        try:
            profile = user.financial_profile
        except FinancialProfile.DoesNotExist:
            return Response({"detail": "Profil financier introuvable."}, status=400)

        solde = Decimal(profile.solde or 0)
        salaire = Decimal(profile.salaire_mensuel or 0)
        fixes = Decimal(profile.depenses_fixes or 0)

        today = timezone.localdate()
        m_start, m_end = _month_bounds(today)

        # 2) Dépenses variables du mois (Expense)
        var_sum = Expense.objects.filter(
            user=user,
            date__gte=m_start,
            date__lt=m_end
        ).aggregate(s=Sum("amount"))["s"] or Decimal("0")

        # 3) Abonnements actifs sur le mois (RecurringExpense)
        # actif si start_date <= fin_mois et (end_date null ou end_date >= debut_mois)
        rec_qs = RecurringExpense.objects.filter(
            user=user,
            active=True,
            start_date__lt=m_end,
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=m_start)
        )

        rec_sum = rec_qs.aggregate(s=Sum("amount"))["s"] or Decimal("0")

        # 4) Marge de sécurité selon priorité
        # (tu peux ajuster les chiffres)
        if priority == "NEED":
            safety_margin = Decimal("50")
        elif priority == "WANT":
            safety_margin = Decimal("150")
        else:  # LUXURY
            safety_margin = Decimal("300")

        # 5) Capacité mensuelle d’épargne estimée
        monthly_capacity = salaire - fixes - var_sum - rec_sum

        warnings = []
        if salaire == 0:
            warnings.append("Salaire = 0 : la capacité d’épargne peut être négative/limitée.")
        if var_sum == 0:
            warnings.append("Aucune dépense variable saisie ce mois : le calcul peut être optimiste.")
        if monthly_capacity <= 0:
            warnings.append("Capacité mensuelle d’épargne <= 0 : il faudra réduire les dépenses ou augmenter les revenus.")

        # 6) Décision maintenant ?
        need_total = price + safety_margin
        if solde >= need_total:
            decision = "BUY_NOW"
            estimated_months = 0
            recommended_monthly = Decimal("0")
        else:
            missing = need_total - solde

            # Si l’utilisateur impose un montant par mois
            if monthly_target is not None and monthly_target > 0:
                recommended_monthly = Decimal(monthly_target)
                estimated_months = _ceil_div(missing, recommended_monthly)
                decision = "WAIT"
            else:
                if monthly_capacity <= 0:
                    decision = "NOT_POSSIBLE"
                    estimated_months = 0
                    recommended_monthly = Decimal("0")
                else:
                    estimated_months = _ceil_div(missing, monthly_capacity)
                    recommended_monthly = monthly_capacity
                    decision = "WAIT"

        # 7) Faisabilité par date souhaitée
        feasible_by_date = None
        months_until = None
        if desired_date:
            # mois approximatifs entre today et desired_date (arrondi)
            dy = (desired_date.year - today.year) * 12 + (desired_date.month - today.month)
            months_until = max(0, dy)
            if decision == "BUY_NOW":
                feasible_by_date = True
            elif decision == "WAIT":
                feasible_by_date = (estimated_months <= months_until)
            else:
                feasible_by_date = False

        # 8) Conseils simples : top catégories dépensées ce mois
        top_categories = []
        qs = Expense.objects.filter(user=user, date__gte=m_start, date__lt=m_end)\
            .values("category__name")\
            .annotate(total=Sum("amount"))\
            .order_by("-total")[:3]
        for row in qs:
            top_categories.append({"category": row["category__name"], "total": row["total"]})

        suggestions = []
        if decision in ("WAIT", "NOT_POSSIBLE") and top_categories:
            c = top_categories[0]
            suggestions.append(
                f"Réduire '{c['category']}' de 50€ / mois peut accélérer ton achat."
            )

        details = {
            "month": str(today)[:7],
            "solde": str(solde),
            "salaire_mensuel": str(salaire),
            "depenses_fixes": str(fixes),
            "depenses_variables_mois": str(var_sum),
            "abonnements_mois": str(rec_sum),
            "safety_margin": str(safety_margin),
            "monthly_capacity": str(monthly_capacity),
            "warnings": warnings,
            "top_categories": top_categories,
            "suggestions": suggestions,
            "desired_date": str(desired_date) if desired_date else None,
            "months_until_desired_date": months_until,
            "feasible_by_desired_date": feasible_by_date,
        }

        # 9) Sauvegarder en DB (historique)
        sim = PurchaseSimulation.objects.create(
            user=user,
            item_name=item_name,
            price=price,
            priority=priority,
            desired_date=desired_date,
            decision=decision,
            estimated_months=estimated_months,
            recommended_monthly_saving=recommended_monthly,
            details=details,
        )

        out = PurchaseSimulationSerializer(sim).data
        return Response(out, status=status.HTTP_201_CREATED)



#-----------------------------------

from rest_framework.permissions import IsAuthenticated

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from datetime import datetime
        from decimal import Decimal
        from django.db.models import Sum
        from django.db import models
        from django.utils import timezone
        from .models import Expense, RecurringExpense, FinancialProfile

        user = request.user

        # 1) Mois ciblé
        month_str = request.query_params.get("month")  # "YYYY-MM"
        today = timezone.localdate()
        if month_str:
            try:
                dt = datetime.strptime(month_str, "%Y-%m")
                target = dt.date().replace(day=1)
            except ValueError:
                return Response({"detail": "month doit être au format YYYY-MM"}, status=400)
        else:
            target = today.replace(day=1)

        # bornes du mois
        m_start = target
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1)

        # 2) Profil
        try:
            profile = user.financial_profile
        except FinancialProfile.DoesNotExist:
            return Response({"detail": "Profil financier introuvable."}, status=400)

        solde = Decimal(profile.solde or 0)
        salaire = Decimal(profile.salaire_mensuel or 0)
        fixes = Decimal(profile.depenses_fixes or 0)

        # 3) Dépenses variables du mois
        var_qs = Expense.objects.filter(user=user, date__gte=m_start, date__lt=m_end)
        var_total = var_qs.aggregate(s=Sum("amount"))["s"] or Decimal("0")

        # 4) Abonnements actifs sur le mois
        rec_qs = RecurringExpense.objects.filter(
            user=user,
            active=True,
            start_date__lt=m_end,
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=m_start)
        )
        rec_total = rec_qs.aggregate(s=Sum("amount"))["s"] or Decimal("0")

        # 5) Répartition par catégories (graph)
        by_category = list(
            var_qs.values("category__name")
                 .annotate(total=Sum("amount"))
                 .order_by("-total")
        )
        # on renomme la clé pour être plus clean côté front
        by_category = [
            {"category": row["category__name"], "total": str(row["total"])}
            for row in by_category
        ]

        # 6) Top 5 dépenses (liste)
        top_expenses = list(
            var_qs.select_related("category")
                 .order_by("-amount")[:5]
                 .values("id", "amount", "date", "description", "category__name")
        )
        top_expenses = [
            {
                "id": r["id"],
                "amount": str(r["amount"]),
                "date": str(r["date"]),
                "description": r["description"],
                "category": r["category__name"],
            }
            for r in top_expenses
        ]

        # 7) Capacité d’épargne estimée
        monthly_capacity = salaire - fixes - var_total - rec_total

        warnings = []
        if salaire == 0:
            warnings.append("Salaire = 0 : le calcul d’épargne est limité.")
        if var_total == 0:
            warnings.append("Aucune dépense variable sur ce mois.")
        if monthly_capacity <= 0:
            warnings.append("Capacité d’épargne <= 0 : réduire dépenses ou augmenter revenus.")

        data = {
            "month": m_start.strftime("%Y-%m"),
            "profile": {
                "solde": str(solde),
                "salaire_mensuel": str(salaire),
                "depenses_fixes": str(fixes),
            },
            "totals": {
                "depenses_variables": str(var_total),
                "abonnements": str(rec_total),
                "capacite_epargne": str(monthly_capacity),
            },
            "by_category": by_category,
            "top_expenses": top_expenses,
            "warnings": warnings,
        }

        return Response(data, status=200)



#-----------------


