"""
PocketSage - Alert Agent
Anticipe les difficultés financières et envoie des alertes proactives.
C'est l'agent qui agit AVANT que le problème arrive.
"""

import time
import os
import json
from google import genai
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tools.storage import get_transactions, get_summary, load_user_data, save_user_data

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


SYSTEM_PROMPT = """
Tu es AlertAgent, l'agent de prévention financière de PocketSage.
Tu anticipes les problèmes financiers AVANT qu'ils arrivent.

TON RÔLE :
1. Analyser le rythme des dépenses en cours de mois
2. Projeter la situation en fin de mois
3. Alerter si le budget risque d'être dépassé
4. Suggérer des arbitrages concrets et réalistes
5. Rappeler les dépenses sociales prévisibles (fin de mois = loyer, etc.)

RÈGLES IMPORTANTES :
- Ne jamais alarmer inutilement
- Toujours proposer une solution concrète avec l'alerte
- Adapter les conseils au contexte africain (pas de carte de crédit, etc.)
- Respecter les priorités culturelles de l'utilisateur
- Répondre dans la langue de l'utilisateur

NIVEAUX D'ALERTE :
- 🟢 VERT : Situation saine, continuer ainsi
- 🟡 JAUNE : Attention, surveiller les dépenses
- 🔴 ROUGE : Danger, action immédiate recommandée
"""


class AlertAgent:
    """
    Agent proactif qui anticipe et prévient les difficultés financières.
    """

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = "gemini-2.0-flash-lite"
        self.system_instruction = SYSTEM_PROMPT

    def _call_with_retry(self, fn, *args, retries=3, wait=30):
        """Appel API avec retry automatique en cas de quota dépassé."""
        for attempt in range(retries):
            try:
                return fn(*args)
            except Exception as e:
                if "429" in str(e) and attempt < retries - 1:
                    console_wait = wait * (attempt + 1)
                    print(f"⏳ Quota atteint. Attente {console_wait}s...")
                    time.sleep(console_wait)
                else:
                    raise

    def _get_month_projection(self, user_id: str) -> dict:
        """
        Projette les dépenses jusqu'à la fin du mois
        basé sur le rythme actuel.
        """
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        summary = get_summary(user_id, current_month)

        # Jours écoulés et restants dans le mois
        days_elapsed = now.day
        days_in_month = 30  # Approximation
        days_remaining = days_in_month - days_elapsed

        # Projection linéaire des dépenses
        daily_spend = summary["depenses"] / max(days_elapsed, 1)
        projected_total = summary["depenses"] + (daily_spend * days_remaining)
        projected_balance = summary["revenus"] - projected_total

        return {
            "current_month": current_month,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
            "current_depenses": summary["depenses"],
            "current_revenus": summary["revenus"],
            "current_solde": summary["solde"],
            "daily_spend_rate": round(daily_spend, 0),
            "projected_month_total": round(projected_total, 0),
            "projected_end_balance": round(projected_balance, 0),
        }

    def check_alerts(self, user_id: str, lang: str = "fr") -> dict:
        """
        Vérifie la situation financière et génère des alertes si nécessaire.

        Retourne :
        {
            "level": "green" | "yellow" | "red",
            "message": str,
            "actions": list[str]
        }
        """
        projection = self._get_month_projection(user_id)

        # Pas assez de données
        if projection["current_depenses"] == 0:
            return {
                "level": "green",
                "message": "",
                "actions": [],
            }

        prompt = f"""
        Analyse cette projection financière et génère une alerte appropriée.
        Réponds en langue : {lang}

        Projection du mois :
        {json.dumps(projection, ensure_ascii=False, indent=2)}

        Réponds UNIQUEMENT avec ce JSON (pas de texte autour) :
        {{
            "level": "green" ou "yellow" ou "red",
            "message": "message d'alerte en {lang}",
            "actions": ["action 1", "action 2", "action 3"]
        }}
        """

        try:
            result = self._call_with_retry(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config={"system_instruction": self.system_instruction},
            )
            text = result.text.strip()

            # Nettoyer le JSON
            import re
            text = re.sub(r"```json|```", "", text).strip()
            alert_data = json.loads(text)
            return alert_data

        except Exception as e:
            return {
                "level": "yellow",
                "message": f"Impossible d'analyser la situation : {e}",
                "actions": [],
            }

    def get_upcoming_expenses(self, user_id: str, lang: str = "fr") -> str:
        """
        Rappelle les dépenses prévisibles à venir
        (loyer fin de mois, tontines, etc.)
        """
        data = load_user_data(user_id)
        tontines = data.get("tontines", [])
        now = datetime.now()
        days_remaining = 30 - now.day

        prompt = f"""
        L'utilisateur a {days_remaining} jours restants dans le mois.
        Tontines enregistrées : {json.dumps(tontines, ensure_ascii=False)}

        Génère un rappel bienveillant des dépenses prévisibles à venir
        (loyer, tontines, courses de fin de mois, etc.)
        en {lang}.
        Sois concis (3-4 lignes max).
        """

        try:
            result = self._call_with_retry(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config={"system_instruction": self.system_instruction},
            )
            return result.text
        except Exception as e:
            return f"Erreur AlertAgent : {e}"
