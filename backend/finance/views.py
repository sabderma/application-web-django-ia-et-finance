from datetime import date
from decimal import Decimal, ROUND_CEILING

from django.db.models import Sum, Q
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Category, Expense, RecurringExpense, PurchaseSimulation, FinancialProfile
from .serializers import (
    CategorySerializer,
    ExpenseSerializer,
    RecurringExpenseSerializer,
    PurchaseSimulationSerializer,
    FinancialProfileSerializer,
    PurchaseSimulateInputSerializer,
    AdviceInputSerializer,
)   

from rest_framework.permissions import IsAuthenticated

from .advice import build_budget_prompt, call_groq
#----------------------
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Category.objects.filter(user=self.request.user).order_by("name")
        type_param = self.request.query_params.get("type")
        if type_param:
            qs = qs.filter(type=type_param)
        return qs
        
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /categories/<id>/ -> détail
    PATCH  /categories/<id>/ -> modifier (ex: renommer, type)
    DELETE /categories/<id>/ -> supprimer
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
# --------------------
# EXPENSES
# --------------------

class ExpenseListCreateView(generics.ListCreateAPIView):
    """
    GET  /expenses/ -> liste
    POST /expenses/ -> créer
    """
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).order_by("-date")


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /expenses/<id>/ -> détail
    PATCH  /expenses/<id>/ -> modifier
    DELETE /expenses/<id>/ -> supprimer
    """
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


# --------------------
# RECURRING EXPENSES
# --------------------

class RecurringExpenseListCreateView(generics.ListCreateAPIView):
    """
    GET  /recurring-expenses/ -> liste
    POST /recurring-expenses/ -> créer
    """
    serializer_class = RecurringExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecurringExpense.objects.filter(user=self.request.user).order_by("-created_at")


class RecurringExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /recurring-expenses/<id>/ -> détail
    PATCH  /recurring-expenses/<id>/ -> modifier
    DELETE /recurring-expenses/<id>/ -> supprimer
    """
    serializer_class = RecurringExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecurringExpense.objects.filter(user=self.request.user)


# --------------------
# PURCHASE SIMULATIONS (HISTORIQUE)
# --------------------

class PurchaseSimulationListView(generics.ListAPIView):
    """
    GET /purchase-simulations/ -> historique
    """
    serializer_class = PurchaseSimulationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseSimulation.objects.filter(user=self.request.user).order_by("-created_at")


class PurchaseSimulationDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /purchase-simulations/<id>/ -> détail
    DELETE /purchase-simulations/<id>/ -> supprimer
    """
    serializer_class = PurchaseSimulationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseSimulation.objects.filter(user=self.request.user)


# --------------------
# FINANCIAL PROFILE (1 profil par user)
# --------------------

class FinancialProfileMeView(generics.RetrieveUpdateAPIView):
    """
    GET   /financial-profile/me/  -> récupérer le profil du user connecté
    PATCH /financial-profile/me/  -> modifier le profil (âge, salaire, statut, etc.)
    """
    serializer_class = FinancialProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
       
        obj, _created = FinancialProfile.objects.get_or_create(user=self.request.user)
        return obj
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
    permission_classes = [IsAuthenticated]

    def post(self, request):

        inp = PurchaseSimulateInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        data = inp.validated_data

        user = request.user
        item_name = data["item_name"]
        price: Decimal = data["price"]
        priority = data["priority"]
        monthly_target = data.get("monthly_saving_target")

        # 1) Profil financier
        try:
            profile = user.financial_profile
        except FinancialProfile.DoesNotExist:
            return Response(
                {"detail": "Profil financier introuvable."},
                status=status.HTTP_400_BAD_REQUEST
            )

        solde = Decimal(profile.solde or 0)
        salaire = Decimal(profile.salaire_mensuel or 0)
        fixes = Decimal(profile.depenses_fixes or 0)

        today = timezone.localdate()
        m_start, m_end = _month_bounds(today)

        # 2) Dépenses variables du mois
        var_sum = Expense.objects.filter(
            user=user,
            date__gte=m_start,
            date__lt=m_end
        ).aggregate(s=Sum("amount"))["s"] or Decimal("0")

        # 3) Abonnements actifs
        rec_qs = RecurringExpense.objects.filter(
            user=user,
            active=True,
            start_date__lt=m_end,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=m_start)
        )

        rec_sum = rec_qs.aggregate(s=Sum("amount"))["s"] or Decimal("0")

        # 4) Marge selon priorité
        if priority == "NEED":
            safety_margin = Decimal("50")
        elif priority == "WANT":
            safety_margin = Decimal("150")
        else:
            safety_margin = Decimal("300")

        # 5) Capacité mensuelle
        monthly_capacity = salaire - fixes - var_sum - rec_sum

        need_total = price + safety_margin

        # 6) Décision
        if solde >= need_total:
            decision = "BUY_NOW"
            estimated_months = 0
            recommended_monthly = Decimal("0")
        else:
            missing = need_total - solde

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

        # 7) Détails simplifiés
        details = {
            "month": str(today)[:7],
            "solde": str(solde),
            "salaire_mensuel": str(salaire),
            "depenses_fixes": str(fixes),
            "depenses_variables_mois": str(var_sum),
            "abonnements_mois": str(rec_sum),
            "safety_margin": str(safety_margin),
            "monthly_capacity": str(monthly_capacity),
        }

        sim = PurchaseSimulation.objects.create(
            user=user,
            item_name=item_name,
            price=price,
            priority=priority,
            decision=decision,
            estimated_months=estimated_months,
            recommended_monthly_saving=recommended_monthly,
            details=details,
        )

        out = PurchaseSimulationSerializer(sim).data
        return Response(out, status=status.HTTP_201_CREATED)
#-----------------------------------

from rest_framework.views import APIView
from rest_framework.response import Response
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

        # 3) Dépenses variables du mois (Expense)
        var_qs = Expense.objects.filter(user=user, date__gte=m_start, date__lt=m_end)
        var_total = var_qs.aggregate(s=Sum("amount"))["s"] or Decimal("0")

        # 4) Abonnements actifs sur le mois (RecurringExpense)
        rec_qs = RecurringExpense.objects.filter(
            user=user,
            active=True,
            start_date__lt=m_end,
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=m_start)
        )
        rec_total = rec_qs.aggregate(s=Sum("amount"))["s"] or Decimal("0")

        # 5) Répartition par catégories (graph) = NORMAL + ABONNEMENT (1 seul graph)
        var_by_cat = list(
            var_qs.values("category__name")
                  .annotate(total=Sum("amount"))
        )

        rec_by_cat = list(
            rec_qs.values("category__name")
                  .annotate(total=Sum("amount"))
        )

        merged = {}

        for row in var_by_cat:
            name = row["category__name"] or "Sans catégorie"
            merged.setdefault(name, {"normal": Decimal("0"), "abonnement": Decimal("0")})
            merged[name]["normal"] += (row["total"] or Decimal("0"))

        for row in rec_by_cat:
            name = row["category__name"] or "Sans catégorie"
            merged.setdefault(name, {"normal": Decimal("0"), "abonnement": Decimal("0")})
            merged[name]["abonnement"] += (row["total"] or Decimal("0"))

        by_category = [
            {
                "category": name,
                "normal_total": str(vals["normal"]),
                "abonnement_total": str(vals["abonnement"]),
                "total": str(vals["normal"] + vals["abonnement"]),
            }
            for name, vals in merged.items()
        ]

        by_category.sort(key=lambda x: Decimal(x["total"]), reverse=True)

        # 6) Top 5 dépenses (liste) - seulement Expense (variables)
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



class CategoryAllListView(generics.ListAPIView):
    """
    GET /categories/all/ -> toutes les catégories
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by("name")
    




class AdviceView(APIView):
    """
    POST /api/advice/
    Body: { "simulation_id": 123 }
    Retour: { "advice_text": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        inp = AdviceInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)

        sim_id = inp.validated_data["simulation_id"]

        sim = PurchaseSimulation.objects.filter(id=sim_id, user=request.user).first()
        if not sim:
            return Response({"detail": "Simulation introuvable."}, status=status.HTTP_404_NOT_FOUND)

        d = sim.details or {}

        summary = {
            "item_name": sim.item_name,
            "price": str(sim.price),
            "priority": sim.priority,
            "decision": sim.decision,
            "estimated_months": sim.estimated_months,
            "recommended_monthly_saving": str(sim.recommended_monthly_saving),

            # chiffres du details (si présents)
            "solde": d.get("solde"),
            "salaire_mensuel": d.get("salaire_mensuel"),
            "depenses_fixes": d.get("depenses_fixes"),
            "depenses_variables_mois": d.get("depenses_variables_mois"),
            "abonnements_mois": d.get("abonnements_mois"),
            "monthly_capacity": d.get("monthly_capacity"),
        }

        prompt = build_budget_prompt(summary)

        try:
            advice_text = call_groq(prompt)
        except Exception as e:
            print("ADVICE ERROR:", repr(e))  # ✅ affiche l'erreur exacte dans le terminal
            return Response(
                {"detail": "Erreur lors de l'appel IA", "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )


        return Response({"advice_text": advice_text}, status=status.HTTP_200_OK)