import os
import requests


def build_budget_prompt(summary: dict) -> str:
    return f"""
Tu es un coach budget personnel.
Ta mission: donner des conseils concrets et chiffrés pour mieux gérer les dépenses et atteindre l'achat plus vite.

Règles:
- Répond en français.
- Donne exactement 6 conseils en liste numérotée.
- Conseils courts (1 à 2 phrases max chacun).
- Utilise des montants (ex: "réduis X de 20€") quand c'est possible.
- Pas de jugement, pas de morale, pas de blabla.

Données utilisateur (résumé):
- Produit: {summary.get("item_name")}
- Prix: {summary.get("price")} €
- Priorité: {summary.get("priority")}
- Décision actuelle: {summary.get("decision")}
- Mois estimés: {summary.get("estimated_months")}
- Épargne conseillée: {summary.get("recommended_monthly_saving")} €

Budget du mois:
- Solde: {summary.get("solde")} €
- Salaire mensuel: {summary.get("salaire_mensuel")} €
- Dépenses fixes: {summary.get("depenses_fixes")} €
- Dépenses variables (mois): {summary.get("depenses_variables_mois")} €
- Abonnements (mois): {summary.get("abonnements_mois")} €
- Capacité mensuelle estimée: {summary.get("monthly_capacity")} €

Répond maintenant.
""".strip()


import json
import requests
from requests.exceptions import RequestException

def call_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY manquante (vérifie .env + load_dotenv)")

    candidates = [
    os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant",
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
     ]

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    last_err = None

    for model in candidates:
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Tu es un coach budget."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }

        try:
            r = requests.post(url, headers=headers, json=body, timeout=60)
        except RequestException as e:
            raise RuntimeError(f"Erreur réseau/SSL Groq: {repr(e)}")

        # log utile
        print("GROQ status:", r.status_code, "model:", model)
        print("GROQ body:", r.text[:500])

        if r.status_code < 400:
            data = r.json()
            if "choices" not in data:
                raise RuntimeError(f"Réponse Groq inattendue: {data}")
            return data["choices"][0]["message"]["content"]

        last_err = f"Groq ({r.status_code}) model='{model}': {r.text}"

        if "model_decommissioned" in r.text:
            continue

        break

    raise RuntimeError(last_err or "Erreur Groq inconnue")