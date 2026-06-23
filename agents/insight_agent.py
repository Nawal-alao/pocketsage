"""
PocketSage - Insight Agent
Analyse les patterns de dépenses et génère des recommandations personnalisées
adaptées au contexte économique d'Afrique de l'Ouest.
"""

import time
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from tools.storage import get_transactions, get_summary

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


SYSTEM_PROMPT = """
Tu es InsightAgent, l'analyste financier de PocketSage.
Tu analyses les habitudes financières des utilisateurs d'Afrique de l'Ouest
et génères des recommandations culturellement adaptées.

CONTEXTE QUE TU COMPRENDS :
- Revenus variables et irréguliers (pas de salaire fixe mensuel)
- Importance des dépenses sociales (tontines, cérémonies)
- Épargne informelle (tirelire, garde chez un proche)
- Mobile Money (MTN, Moov) comme outil principal
- Contraintes économiques réelles du terrain

TON RÔLE :
1. Identifier les patterns de dépenses (où va l'argent ?)
2. Détecter les anomalies (dépense inhabituelle ce mois)
3. Comparer mois par mois quand les données le permettent
4. Générer des conseils RÉALISTES et CULTURELLEMENT ADAPTÉS
5. Ne jamais juger les dépenses sociales ou culturelles

STYLE DE RÉPONSE :
- Chaleureux, comme un ami de confiance
- Concret avec des chiffres précis en FCFA
- Conseils actionnables, pas théoriques
- Toujours dans la langue de l'utilisateur
"""


class InsightAgent:
    """
    Agent spécialisé dans l'analyse des patterns financiers.
    """

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite",
            system_instruction=SYSTEM_PROMPT,
        )

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

    def analyze(self, user_id: str, month: str = None, lang: str = "fr") -> str:
        """
        Analyse les transactions et génère des insights personnalisés.

        Args:
            user_id: Identifiant utilisateur
            month: Mois à analyser (YYYY-MM), None = tout
            lang: Langue de réponse (fr, en, fon, yo)

        Returns:
            Analyse en langage naturel
        """
        transactions = get_transactions(user_id, month)
        summary = get_summary(user_id, month)

        if not transactions:
            messages = {
                "fr": "Pas encore de transactions à analyser. Commence par enregistrer tes dépenses !",
                "en": "No transactions to analyze yet. Start by recording your expenses!",
                "fon": "Alɔgba lɛ kpɔ o. Bló nú ɖó wěɖexámɛ towe lɛ jí!",
                "yo": "Ko si awọn iṣowo lati ṣe atupale. Bẹrẹ gbigbasilẹ awọn inawo rẹ!",
            }
            return messages.get(lang, messages["fr"])

        # Préparer les données pour l'analyse
        categories = {}
        sources = {}
        for t in transactions:
            cat = t.get("categorie", "autre")
            categories[cat] = categories.get(cat, 0) + t.get("montant", 0)
            src = t.get("source", "cash")
            sources[src] = sources.get(src, 0) + 1

        analysis_data = {
            "summary": summary,
            "categories": categories,
            "payment_sources": sources,
            "transactions_count": len(transactions),
            "month": month,
        }

        prompt = f"""
        Analyse ces données financières et génère des insights utiles.
        Réponds en : {lang}

        Données :
        {json.dumps(analysis_data, ensure_ascii=False, indent=2)}

        Génère :
        1. Un résumé de la situation financière
        2. Les 2-3 postes de dépenses principaux
        3. Un conseil pratique et réaliste
        4. Un encouragement personnalisé
        """

        try:
            result = self._call_with_retry(self.model.generate_content, prompt)
            return result.text
        except Exception as e:
            return f"Erreur InsightAgent : {e}"

    def detect_anomalies(self, user_id: str, lang: str = "fr") -> str:
        """
        Détecte les dépenses inhabituelles ou anomalies financières.
        """
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        transactions = get_transactions(user_id, current_month)

        if len(transactions) < 3:
            return ""

        prompt = f"""
        Voici les transactions du mois en cours :
        {json.dumps(transactions, ensure_ascii=False, indent=2)}

        Y a-t-il des dépenses inhabituellement élevées ou des anomalies ?
        Si oui, signale-les de façon bienveillante en {lang}.
        Si tout semble normal, réponds avec un message court positif.
        """

        try:
            result = self._call_with_retry(self.model.generate_content, prompt)
            return result.text
        except Exception as e:
            return f"Erreur détection anomalies : {e}"