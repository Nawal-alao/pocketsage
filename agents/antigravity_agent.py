"""
PocketSage - Antigravity Agent
Utilise le modèle Antigravity de Google pour un raisonnement financier
non-linéaire et multi-scénarios.

Antigravity explore plusieurs chemins de raisonnement en parallèle
avant de choisir la meilleure recommandation — idéal pour les décisions
financières complexes où plusieurs options s'affrontent.

Exemple : "Est-ce que j'achète une moto maintenant ou j'attends ?"
→ Antigravity explore : impact budget, alternatives, timing optimal,
  risques, opportunités — et synthétise la meilleure réponse.
"""

import os
import json
from google import genai
from dotenv import load_dotenv
from tools.storage import get_summary, get_transactions, load_user_data

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

ANTIGRAVITY_MODEL = "antigravity-preview-05-2026"

SYSTEM_PROMPT = """
Tu es FinanceAdvisor, le conseiller financier avancé de PocketSage.
Tu utilises un raisonnement multi-scénarios pour aider les utilisateurs
d'Afrique de l'Ouest à prendre de meilleures décisions financières.

TON APPROCHE UNIQUE :
Pour chaque décision financière complexe, tu explores PLUSIEURS scénarios :

SCÉNARIO A : Si l'utilisateur fait X maintenant
SCÉNARIO B : Si l'utilisateur attend N mois
SCÉNARIO C : Alternative créative adaptée au contexte africain
SYNTHÈSE : La recommandation optimale avec justification

CONTEXTE QUE TU MAÎTRISES :
- Économie informelle d'Afrique de l'Ouest
- Revenus variables et irréguliers
- Mobile Money (MTN, Moov) comme outil principal
- Tontines comme mécanisme d'épargne collectif
- Dépenses sociales importantes et non-négociables
- Marché de l'occasion très développé
- Crédit informel (famille, amis, tontine)

RÈGLES :
- Toujours proposer au moins 3 scénarios
- Chiffrer chaque scénario en FCFA quand possible
- Adapter les conseils à la réalité du terrain
- Ne jamais suggérer des solutions inaccessibles
- Répondre dans la langue de l'utilisateur
- Être direct et concret, pas théorique
"""


class AntigravityAgent:
    """
    Agent de décision financière avancée utilisant Antigravity.
    Explore plusieurs scénarios avant de recommander.
    """

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = ANTIGRAVITY_MODEL
        self.system_instruction = SYSTEM_PROMPT
        self.available = True

        try:
            # On vérifie seulement que le modèle est accessible en créant une requête
            self.client.models.compute_tokens(
                model=self.model_name,
                contents=["Validation du modèle Antigravity"],
            )
        except Exception:
            self.available = False
            self.model_name = "gemini-2.0-flash-lite"
            print(f"[AntigravityAgent] ⚠️ Antigravity indisponible, fallback activé")

    def analyze_decision(
        self,
        user_id: str,
        question: str,
        lang: str = "fr"
    ) -> dict:
        """
        Analyse une décision financière complexe avec raisonnement multi-scénarios.

        Args:
            user_id: Identifiant utilisateur
            question: La décision à analyser
            lang: Langue de réponse

        Returns:
            {
                "scenarios": list,
                "recommendation": str,
                "reasoning": str,
                "model_used": str,
            }
        """
        # Charger le contexte financier de l'utilisateur
        summary = get_summary(user_id)
        data = load_user_data(user_id)
        transactions = get_transactions(user_id)

        # Calculer quelques métriques utiles
        total_depenses = summary.get("depenses", 0)
        total_revenus = summary.get("revenus", 0)
        solde = summary.get("solde", 0)
        nb_tx = summary.get("nb_transactions", 0)

        # Catégories de dépenses
        categories = {}
        for tx in transactions:
            cat = tx.get("categorie", "autre")
            categories[cat] = categories.get(cat, 0) + tx.get("montant", 0)

        context = {
            "solde_actuel": solde,
            "revenus_ce_mois": total_revenus,
            "depenses_ce_mois": total_depenses,
            "nb_transactions": nb_tx,
            "categories_depenses": categories,
            "tontines": data.get("tontines", []),
            "profil": data.get("profile", {}),
        }

        prompt = f"""
L'utilisateur pose cette question financière :
"{question}"

Voici son contexte financier actuel :
{json.dumps(context, ensure_ascii=False, indent=2)}

Réponds en langue : {lang}

Structure ta réponse EXACTEMENT ainsi (JSON uniquement, pas de texte autour) :
{{
    "scenarios": [
        {{
            "label": "Scénario A — [titre court]",
            "description": "Description du scénario",
            "avantages": ["avantage 1", "avantage 2"],
            "risques": ["risque 1", "risque 2"],
            "impact_fcfa": "Impact estimé en FCFA"
        }},
        {{
            "label": "Scénario B — [titre court]",
            "description": "Description du scénario",
            "avantages": ["avantage 1", "avantage 2"],
            "risques": ["risque 1", "risque 2"],
            "impact_fcfa": "Impact estimé en FCFA"
        }},
        {{
            "label": "Scénario C — [alternative créative]",
            "description": "Description du scénario",
            "avantages": ["avantage 1", "avantage 2"],
            "risques": ["risque 1", "risque 2"],
            "impact_fcfa": "Impact estimé en FCFA"
        }}
    ],
    "recommendation": "La recommandation finale claire et directe",
    "reasoning": "Explication courte du raisonnement (2-3 phrases)",
    "urgency": "immediate | attendre | flexible"
}}
"""

        try:
            result = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"system_instruction": self.system_instruction},
            )
            text = result.text.strip()

            # Nettoyer le JSON
            import re
            text = re.sub(r"```json|```", "", text).strip()
            parsed = json.loads(text)
            parsed["model_used"] = ANTIGRAVITY_MODEL if self.available else "gemini-2.0-flash-lite (fallback)"
            return parsed

        except json.JSONDecodeError:
            # Retourner la réponse brute si le JSON est malformé
            return {
                "scenarios": [],
                "recommendation": result.text if 'result' in locals() else "Erreur",
                "reasoning": "",
                "urgency": "flexible",
                "model_used": ANTIGRAVITY_MODEL if self.available else "fallback",
            }
        except Exception as e:
            return {
                "scenarios": [],
                "recommendation": f"Erreur AntigravityAgent : {e}",
                "reasoning": "",
                "urgency": "flexible",
                "model_used": "error",
            }

    def quick_advice(self, user_id: str, message: str, lang: str = "fr") -> str:
        """
        Conseil rapide pour des questions simples ne nécessitant pas
        une analyse multi-scénarios complète.
        """
        summary = get_summary(user_id)

        prompt = f"""
Contexte financier : solde={summary.get('solde', 0)} FCFA,
revenus={summary.get('revenus', 0)} FCFA,
dépenses={summary.get('depenses', 0)} FCFA ce mois.

Question : {message}

Donne un conseil court, pratique et adapté au contexte africain.
Réponds en {lang}. Maximum 4 phrases.
"""
        try:
            result = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"system_instruction": self.system_instruction},
            )
            return result.text
        except Exception as e:
            return f"Erreur : {e}"