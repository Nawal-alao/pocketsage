"""
PocketSage - Orchestrator Agent
Le cerveau central qui reçoit chaque message, détecte l'intention
et route vers le bon sous-agent.
Supporte : Français, Anglais, Fon, Yoruba
"""
import time
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from .budget_agent import BudgetAgent
from .insight_agent import InsightAgent
from .alert_agent import AlertAgent

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


SYSTEM_PROMPT = """
Tu es l'Orchestrator de PocketSage, un assistant financier personnel
conçu pour les utilisateurs d'Afrique de l'Ouest.

TON RÔLE UNIQUE :
Analyser chaque message et décider quel agent appeler :

1. BUDGET_AGENT → si l'utilisateur veut :
   - Enregistrer une dépense ("j'ai dépensé", "m'a coûté", "j'ai payé")
   - Enregistrer un revenu ("j'ai reçu", "on m'a payé", "j'ai gagné")
   - Voir son solde ou résumé ("combien j'ai dépensé", "mon solde")

2. INSIGHT_AGENT → si l'utilisateur veut :
   - Analyser ses habitudes ("analyse mes dépenses", "où va mon argent")
   - Obtenir des conseils ("comment économiser", "donne-moi des conseils")
   - Comparer des périodes ("ce mois vs le mois dernier")

3. ALERT_AGENT → si l'utilisateur veut :
   - Vérifier les alertes ("ai-je des alertes", "ma situation ce mois")
   - Voir les dépenses à venir ("qu'est-ce que j'ai à payer")
   - Projection de fin de mois ("vais-je tenir jusqu'à la fin du mois")

4. GENERAL → si c'est une question générale ou une salutation

DÉTECTION DE LANGUE :
Détecte automatiquement la langue du message :
- Français → lang: "fr"
- Anglais → lang: "en"
- Fon → lang: "fon"
- Yoruba → lang: "yo"

RÉPONSE OBLIGATOIRE en JSON uniquement :
{
    "intent": "budget" | "insight" | "alert" | "general",
    "lang": "fr" | "en" | "fon" | "yo",
    "month": "YYYY-MM" | null,
    "confidence": 0.0 à 1.0,
    "general_response": "réponse si intent=general, sinon null"
}
"""

WELCOME_MESSAGES = {
    "fr": """👋 Bonjour ! Je suis **PocketSage**, ton assistant financier personnel.

Je comprends ta réalité : revenus variables, Mobile Money, tontines, dépenses sociales...
Je suis là pour t'aider à mieux gérer ton argent, simplement.

Tu peux me dire des choses comme :
- *"J'ai dépensé 2500 FCFA au marché ce matin"*
- *"MTN m'a crédité 15 000 FCFA"*
- *"Analyse mes dépenses de ce mois"*
- *"Est-ce que je vais tenir jusqu'à la fin du mois ?"*

Comment puis-je t'aider aujourd'hui ? 😊""",

    "en": """👋 Hello! I'm **PocketSage**, your personal finance assistant.

I understand your reality: variable income, Mobile Money, tontines, social expenses...
I'm here to help you manage your money, simply.

You can tell me things like:
- *"I spent 2500 FCFA at the market this morning"*
- *"MTN credited me 15,000 FCFA"*
- *"Analyze my expenses this month"*
- *"Will I make it to the end of the month?"*

How can I help you today? 😊""",

    "fon": """👋 Kudo! Un nyɔnu **PocketSage**, d'asìgán towe tɔn.

Un tuùn nǔ e ɖò ayǐ towe mɛ é: xɔsuklɛ́nmɛ e na lɛ́ lɛ, Mobile Money, tontines...
Un ɖó ayi wu bló nú a na sixu se alɔdo tɔn ɖò xɔ akwɛ towe mɛ.

A sixu ɖɔ nǔ ɖé lɛ bɔ un na tuùn:
- *"Un sɔ́ 2500 FCFA dó azan jɛjɛ"*
- *"MTN na mì 15 000 FCFA"*
- *"Kpɔ́n nǔ e un sɔ́ dó é"*

Etɛ un ka na d'alɔ we ɖè égbé? 😊""",

    "yo": """👋 Ẹ káàárọ̀! Mo jẹ **PocketSage**, olùrànlọ́wọ́ inawo ara ẹni rẹ.

Mo ye ohun tí ó ṣẹlẹ̀ nínú ìgbésí ayé rẹ: owó tí kò dúró ṣinṣin, Mobile Money, tontines...
Mo wà láti ràn ọ́ lọ́wọ́ láti ṣàkóso owó rẹ, rọrùn.

O lè sọ fún mi pé:
- *"Moná 2500 FCFA ní ọjà owurọ̀"*
- *"MTN fi 15 000 FCFA sí account mi"*
- *"Ṣe àyẹ̀wò àwọn inawo mi oṣù yìí"*

Báwo ni mo ṣe lè ràn ọ́ lọ́wọ́ lónìí? 😊""",
}


class OrchestratorAgent:
    """
    Agent principal qui route les messages vers les bons sous-agents.
    Point d'entrée unique pour toutes les interactions utilisateur.
    """

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite",
            system_instruction=SYSTEM_PROMPT,
        )
        # Initialisation des sous-agents
        self.budget_agent = BudgetAgent()
        self.insight_agent = InsightAgent()
        self.alert_agent = AlertAgent()

        # Langue par défaut par utilisateur
        self.user_langs = {}

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

    def _detect_intent(self, message: str) -> dict:
        """
        Analyse le message et retourne l'intention détectée.
        """
        try:
            result = self._call_with_retry(self.model.generate_content, message)
            text = result.text.strip()

            import re
            text = re.sub(r"```json|```", "", text).strip()
            return json.loads(text)

        except Exception as e:
            return {
                "intent": "general",
                "lang": "fr",
                "month": None,
                "confidence": 0.5,
                "general_response": f"Je n'ai pas bien compris. Peux-tu reformuler ? ({e})",
            }

    def welcome(self, user_id: str, lang: str = "fr") -> str:
        """Retourne le message de bienvenue dans la langue choisie."""
        self.user_langs[user_id] = lang
        return WELCOME_MESSAGES.get(lang, WELCOME_MESSAGES["fr"])

    def process(self, user_id: str, message: str) -> dict:
        """
        Point d'entrée principal. Traite un message et retourne une réponse.

        Retourne :
        {
            "response": str,
            "intent": str,
            "lang": str,
            "agent_used": str,
            "data": dict | None,
        }
        """
        # Détecter l'intention
        intent_data = self._detect_intent(message)
        intent = intent_data.get("intent", "general")
        lang = intent_data.get("lang", self.user_langs.get(user_id, "fr"))
        month = intent_data.get("month", None)

        # Mémoriser la langue de l'utilisateur
        self.user_langs[user_id] = lang

        # Router vers le bon agent
        if intent == "budget":
            result = self.budget_agent.process(user_id, message)
            return {
                "response": result["response"],
                "intent": intent,
                "lang": lang,
                "agent_used": "BudgetAgent",
                "data": {
                    "transaction_saved": result["transaction_saved"],
                    "transaction": result["transaction"],
                },
            }

        elif intent == "insight":
            response = self.insight_agent.analyze(user_id, month, lang)
            return {
                "response": response,
                "intent": intent,
                "lang": lang,
                "agent_used": "InsightAgent",
                "data": None,
            }

        elif intent == "alert":
            alert = self.alert_agent.check_alerts(user_id, lang)
            upcoming = self.alert_agent.get_upcoming_expenses(user_id, lang)
            full_response = alert.get("message", "") + "\n\n" + upcoming
            return {
                "response": full_response.strip(),
                "intent": intent,
                "lang": lang,
                "agent_used": "AlertAgent",
                "data": {
                    "alert_level": alert.get("level", "green"),
                    "actions": alert.get("actions", []),
                },
            }

        else:
            # Réponse générale
            general_response = intent_data.get("general_response") or WELCOME_MESSAGES.get(lang, WELCOME_MESSAGES["fr"])
            return {
                "response": general_response,
                "intent": "general",
                "lang": lang,
                "agent_used": "Orchestrator",
                "data": None,
            }