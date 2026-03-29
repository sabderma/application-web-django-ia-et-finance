from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class MLPredictFromProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from finance.models import FinancialProfile
        from .predict import predict_depense

        # 1) Profil utilisateur
        try:
            profile = request.user.financial_profile
        except FinancialProfile.DoesNotExist:
            return Response(
                {"detail": "Profil financier introuvable."},
                status=400
            )

        # 2) Données depuis BDD
        age = profile.age
        salaire_mensuel = float(profile.salaire_mensuel or 0)
        statut = profile.statut

        # 3) Prédiction ML
        pred = predict_depense(
            age=age,
            salaire_mensuel=salaire_mensuel,
            statut=statut,
        )

        return Response({
            "depense_mensuelle_predite": round(float(pred), 2)
        })
