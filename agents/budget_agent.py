"""
PocketSage - Budget Agent
Responsable de l'enregistrement des transactions via conversation naturelle.
Comprend le Français, l'Anglais, le Fon et le Yoruba.
"""

import time
import os
from google import genai
from dotenv import load_dotenv
from tools.storage import add_transaction, get_summary

load_dotenv()


SYSTEM_PROMPT = """
Tu es BudgetAgent, le sous-agent financier de PocketSage.
Tu aides les utilisateurs d'Afrique de l'Ouest à enregistrer leurs dépenses et revenus.

CONTEXTE ÉCONOMIQUE QUE TU COMPRENDS :
- Monnaie : Franc CFA (FCFA)
- Paiements : cash, MTN Mobile Money, Moov Money, virement bancaire
- Revenus irréguliers : commerce, artisanat, agriculture, freelance
- Dépenses sociales : tontines, baptêmes, funérailles, cérémonies
- Langues : Français, Anglais, Fon, Yoruba

TON RÔLE :
1. Extraire les informations d'une transaction depuis le message de l'utilisateur
2. Classifier automatiquement la catégorie
3. Identifier la source de paiement (cash/MTN/Moov/banque)
4. Confirmer avec l'utilisateur avant d'enregistrer
5. Répondre TOUJOURS dans la même langue que l'utilisateur

CATÉGORIES DISPONIBLES :
- alimentation, transport, logement, santé, éducation
- social (tontines, cérémonies), commerce, agriculture
- électronique, habillement, loisirs, autre

FORMAT DE RÉPONSE :
Quand tu identifies une transaction, réponds avec ce JSON dans ta réponse :
<transaction>
{
  "type": "depense" ou "revenu",
  "montant": nombre,
  "categorie": string,
  "description": string,
  "source": "cash" ou "mtn" ou "moov" ou "banque"
}
</transaction>

Puis ajoute une confirmation en langage naturel dans la langue de l'utilisateur.
"""


class BudgetAgent:
    """
    Agent spécialisé dans la saisie conversationnelle des transactions.
    Supporte Français, Anglais, Fon, Yoruba.
    """

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = "gemini-2.0-flash-lite"
        self.system_instruction = SYSTEM_PROMPT
        self.chat_sessions = {}  # user_id -> session

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

    def _get_session(self, user_id: str):
        """Récupère ou crée une session de chat pour l'utilisateur."""
        if user_id not in self.chat_sessions:
            self.chat_sessions[user_id] = self.client.chats.create(
                model=self.model_name,
                config={"system_instruction": self.system_instruction},
                history=[],
            )
        return self.chat_sessions[user_id]

    def _extract_transaction(self, text: str) -> dict | None:
        """
        Extrait le JSON de transaction depuis la réponse du modèle.
        Retourne None si aucune transaction détectée.
        """
        import re, json
        match = re.search(r"<transaction>(.*?)</transaction>", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                return None
        return None

    def process(self, user_id: str, message: str) -> dict:
        """
        Traite un message utilisateur et enregistre la transaction si détectée.

        Retourne :
        {
            "response": str,           # Réponse en langage naturel
            "transaction_saved": bool, # True si transaction enregistrée
            "transaction": dict | None # Données de la transaction
        }
        """
        session = self._get_session(user_id)

        try:
            result = self._call_with_retry(
                session.send_message,
                message,
                {
                    "config": {
                        "system_instruction": self.system_instruction,
                    }
                },
            )
            response_text = result.text

            # Extraire la transaction si présente
            transaction = self._extract_transaction(response_text)
            saved = False

            if transaction:
                saved = add_transaction(user_id, transaction)

            # Nettoyer la réponse (enlever le bloc JSON)
            import re
            clean_response = re.sub(
                r"<transaction>.*?</transaction>",
                "",
                response_text,
                flags=re.DOTALL
            ).strip()

            return {
                "response": clean_response,
                "transaction_saved": saved,
                "transaction": transaction,
            }

        except Exception as e:
            return {
                "response": f"Erreur BudgetAgent : {e}",
                "transaction_saved": False,
                "transaction": None,
            }

    def get_summary_message(self, user_id: str, month: str = None) -> str:
        """Génère un résumé financier en langage naturel."""
        summary = get_summary(user_id, month)
        prompt = f"""
        Voici le résumé financier de l'utilisateur :
        - Revenus : {summary['revenus']} FCFA
        - Dépenses : {summary['depenses']} FCFA
        - Solde : {summary['solde']} FCFA
        - Nombre de transactions : {summary['nb_transactions']}

        Génère un message chaleureux et encourageant qui résume cette situation.
        Utilise la langue de l'utilisateur (français par défaut).
        """
        session = self._get_session(user_id)
        result = self._call_with_retry(session.send_message, prompt)
        return result.text