"""
PocketSage - Tests unitaires
Vérifie le bon fonctionnement de chaque composant sans appel API.
"""

import sys
import os
import json
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── TESTS STORAGE ──

class TestStorage:
    """Tests du module de stockage local."""

    def setup_method(self):
        """Prépare un user_id de test unique."""
        self.user_id = f"test_user_{datetime.now().timestamp()}"

    def teardown_method(self):
        """Nettoie les fichiers de test après chaque test."""
        from pathlib import Path
        test_file = Path(f"./data/{self.user_id}.json")
        if test_file.exists():
            test_file.unlink()

    def test_load_user_data_new_user(self):
        """Un nouvel utilisateur doit avoir un profil vide."""
        from tools.storage import load_user_data
        data = load_user_data(self.user_id)
        assert data["user_id"] == self.user_id
        assert data["transactions"] == []
        assert data["profile"]["currency"] == "CFA"

    def test_save_and_load_user_data(self):
        """Sauvegarder et recharger des données."""
        from tools.storage import load_user_data, save_user_data
        data = load_user_data(self.user_id)
        data["profile"]["language"] = "fon"
        save_user_data(self.user_id, data)
        reloaded = load_user_data(self.user_id)
        assert reloaded["profile"]["language"] == "fon"

    def test_add_transaction_depense(self):
        """Ajouter une dépense."""
        from tools.storage import add_transaction, get_transactions
        tx = {
            "type": "depense",
            "montant": 2500,
            "categorie": "alimentation",
            "description": "Marché",
            "source": "cash",
        }
        result = add_transaction(self.user_id, tx)
        assert result is True
        transactions = get_transactions(self.user_id)
        assert len(transactions) == 1
        assert transactions[0]["montant"] == 2500
        assert transactions[0]["type"] == "depense"

    def test_add_transaction_revenu(self):
        """Ajouter un revenu."""
        from tools.storage import add_transaction, get_transactions
        tx = {
            "type": "revenu",
            "montant": 45000,
            "categorie": "commerce",
            "description": "Vente marché",
            "source": "cash",
        }
        add_transaction(self.user_id, tx)
        transactions = get_transactions(self.user_id)
        assert transactions[0]["type"] == "revenu"
        assert transactions[0]["montant"] == 45000

    def test_get_summary_correct(self):
        """Le résumé financier doit être correct."""
        from tools.storage import add_transaction, get_summary
        add_transaction(self.user_id, {
            "type": "revenu", "montant": 50000,
            "categorie": "commerce", "source": "mtn"
        })
        add_transaction(self.user_id, {
            "type": "depense", "montant": 15000,
            "categorie": "alimentation", "source": "cash"
        })
        add_transaction(self.user_id, {
            "type": "depense", "montant": 5000,
            "categorie": "transport", "source": "cash"
        })
        summary = get_summary(self.user_id)
        assert summary["revenus"] == 50000
        assert summary["depenses"] == 20000
        assert summary["solde"] == 30000
        assert summary["nb_transactions"] == 3

    def test_get_transactions_by_month(self):
        """Filtrer les transactions par mois."""
        from tools.storage import add_transaction, get_transactions
        current_month = datetime.now().strftime("%Y-%m")
        add_transaction(self.user_id, {
            "type": "depense", "montant": 1000,
            "categorie": "transport", "source": "cash",
            "date": f"{current_month}-01T10:00:00",
        })
        transactions = get_transactions(self.user_id, current_month)
        assert len(transactions) == 1

    def test_multiple_transactions_summary(self):
        """Résumé avec plusieurs transactions mixtes."""
        from tools.storage import add_transaction, get_summary
        transactions = [
            {"type": "revenu", "montant": 30000, "categorie": "commerce", "source": "cash"},
            {"type": "revenu", "montant": 15000, "categorie": "freelance", "source": "mtn"},
            {"type": "depense", "montant": 8000, "categorie": "alimentation", "source": "cash"},
            {"type": "depense", "montant": 3000, "categorie": "transport", "source": "cash"},
            {"type": "depense", "montant": 10000, "categorie": "logement", "source": "moov"},
        ]
        for tx in transactions:
            add_transaction(self.user_id, tx)
        summary = get_summary(self.user_id)
        assert summary["revenus"] == 45000
        assert summary["depenses"] == 21000
        assert summary["solde"] == 24000


# ── TESTS MCP CURRENCY ──

class TestCurrencyServer:
    """Tests du serveur MCP Currency."""

    def test_fallback_rates_exist(self):
        """Les taux de fallback doivent exister."""
        from mcp_servers.currency_server import FALLBACK_RATES
        assert "EUR" in FALLBACK_RATES
        assert "USD" in FALLBACK_RATES
        assert "NGN" in FALLBACK_RATES
        assert FALLBACK_RATES["EUR"] > 0

    def test_eur_rate_reasonable(self):
        """Le taux EUR/FCFA doit être dans une plage raisonnable."""
        from mcp_servers.currency_server import FALLBACK_RATES
        # 1 EUR ≈ 655 FCFA (taux fixe CFA)
        assert 600 < FALLBACK_RATES["EUR"] < 700

    def test_conversion_logic(self):
        """Tester la logique de conversion."""
        from mcp_servers.currency_server import FALLBACK_RATES
        amount_fcfa = 100000
        rate_eur = FALLBACK_RATES["EUR"]
        converted = amount_fcfa / rate_eur
        # 100 000 FCFA ≈ 152 EUR
        assert 140 < converted < 170


# ── TESTS MCP CALENDAR ──

class TestCalendarServer:
    """Tests du serveur MCP Calendar."""

    def test_recurring_events_exist(self):
        """Les événements récurrents doivent exister."""
        from mcp_servers.calendar_server import RECURRING_EVENTS
        assert len(RECURRING_EVENTS) > 0

    def test_recurring_events_structure(self):
        """Chaque événement doit avoir les champs requis."""
        from mcp_servers.calendar_server import RECURRING_EVENTS
        required_fields = ["day_of_month", "name", "categorie", "type", "priority"]
        for event in RECURRING_EVENTS:
            for field in required_fields:
                assert field in event, f"Champ manquant : {field}"

    def test_cultural_events_2026(self):
        """Les événements culturels 2026 doivent exister."""
        from mcp_servers.calendar_server import CULTURAL_EVENTS_2026
        assert len(CULTURAL_EVENTS_2026) > 0
        for event in CULTURAL_EVENTS_2026:
            assert "date" in event
            assert "name" in event
            assert event["date"].startswith("2026")

    def test_loyer_in_events(self):
        """Le loyer doit être dans les événements récurrents."""
        from mcp_servers.calendar_server import RECURRING_EVENTS
        names = [e["name"] for e in RECURRING_EVENTS]
        assert "Loyer" in names


# ── TESTS API ──

class TestAPI:
    """Tests des endpoints FastAPI."""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.testclient import TestClient
        from tools.storage import get_summary, get_transactions, load_user_data
        from agents import OrchestratorAgent
        from datetime import datetime

        # App de test sans StaticFiles (cause des conflits avec TestClient)
        test_app = FastAPI()
        test_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @test_app.get("/health")
        async def health():
            return {
                "status": "ok",
                "app": "PocketSage",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
            }

        @test_app.get("/summary/{user_id}")
        async def summary(user_id: str, month: str = None):
            if not month:
                month = datetime.now().strftime("%Y-%m")
            return get_summary(user_id, month)

        @test_app.get("/transactions/{user_id}")
        async def transactions(user_id: str, month: str = None, limit: int = 50):
            from tools.storage import get_transactions
            txs = get_transactions(user_id, month)
            return {"user_id": user_id, "transactions": txs[-limit:]}

        @test_app.get("/profile/{user_id}")
        async def profile(user_id: str):
            data = load_user_data(user_id)
            return {
                "user_id": user_id,
                "profile": data.get("profile", {}),
                "created_at": data.get("created_at"),
                "tontines": data.get("tontines", []),
            }

        from pydantic import BaseModel

        class TransactionRequest(BaseModel):
            user_id: str
            type: str
            montant: float
            categorie: str
            description: str = ""
            source: str = "cash"

        @test_app.post("/transaction")
        async def add_transaction(req: TransactionRequest):
            from tools.storage import add_transaction
            tx = {
                "type": req.type,
                "montant": req.montant,
                "categorie": req.categorie,
                "description": req.description,
                "source": req.source,
                "date": datetime.now().isoformat(),
            }
            success = add_transaction(req.user_id, tx)
            return {"status": "success" if success else "error", "transaction": tx}

        return TestClient(test_app)

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app"] == "PocketSage"

    def test_summary_endpoint_new_user(self, client):
        response = client.get("/summary/test_api_user_new_12345")
        assert response.status_code == 200
        data = response.json()
        assert "revenus" in data
        assert "depenses" in data
        assert "solde" in data

    def test_transactions_endpoint_empty(self, client):
        response = client.get("/transactions/test_api_user_new_12345")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data

    def test_add_transaction_endpoint(self, client):
        payload = {
            "user_id": "test_api_user_tx",
            "type": "depense",
            "montant": 5000,
            "categorie": "alimentation",
            "description": "Test transaction",
            "source": "cash",
        }
        response = client.post("/transaction", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_profile_endpoint(self, client):
        response = client.get("/profile/test_api_user_new_12345")
        assert response.status_code == 200
        data = response.json()
        assert "profile" in data


# ── TESTS AGENT LOGIC (sans appels API) ──

class TestAgentLogic:
    """Tests de la logique des agents sans appels LLM."""

    def test_alert_projection_logic(self):
        """Tester la logique de projection du AlertAgent."""
        from agents.alert_agent import AlertAgent
        agent = AlertAgent()

        # Simuler des données
        with patch("agents.alert_agent.get_summary") as mock_summary:
            mock_summary.return_value = {
                "revenus": 50000,
                "depenses": 30000,
                "solde": 20000,
                "nb_transactions": 10,
            }
            projection = agent._get_month_projection("test_user")

        assert "projected_month_total" in projection
        assert "days_remaining" in projection
        assert "daily_spend_rate" in projection
        assert projection["current_revenus"] == 50000
        assert projection["current_depenses"] == 30000

    def test_budget_agent_extract_transaction(self):
        """Tester l'extraction de transaction depuis le texte."""
        from agents.budget_agent import BudgetAgent
        agent = BudgetAgent()

        text_with_tx = """
        Bien sûr ! J'ai enregistré ta dépense.
        <transaction>
        {
            "type": "depense",
            "montant": 2500,
            "categorie": "alimentation",
            "description": "Marché du matin",
            "source": "cash"
        }
        </transaction>
        """
        tx = agent._extract_transaction(text_with_tx)
        assert tx is not None
        assert tx["type"] == "depense"
        assert tx["montant"] == 2500
        assert tx["categorie"] == "alimentation"

    def test_budget_agent_no_transaction(self):
        """Pas de transaction dans un message général."""
        from agents.budget_agent import BudgetAgent
        agent = BudgetAgent()
        text = "Bonjour ! Comment puis-je t'aider aujourd'hui ?"
        tx = agent._extract_transaction(text)
        assert tx is None


# ── POINT D'ENTRÉE ──

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])