"""
PocketSage - Storage Tool
Gestion locale et sécurisée des données utilisateur.
Aucune donnée ne quitte l'appareil de l'utilisateur.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
DATA_DIR.mkdir(exist_ok=True)


def _get_user_file(user_id: str) -> Path:
    """Retourne le chemin du fichier de données d'un utilisateur."""
    return DATA_DIR / f"{user_id}.json"


def load_user_data(user_id: str) -> dict:
    """
    Charge les données financières d'un utilisateur.
    Crée un profil vide si l'utilisateur est nouveau.
    """
    file = _get_user_file(user_id)
    if not file.exists():
        return {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "profile": {
                "language": "fr",
                "currency": "CFA",
                "income_type": "variable",  # variable | fixed
            },
            "transactions": [],
            "budgets": {},
            "alerts": [],
            "tontines": [],
        }
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_data(user_id: str, data: dict) -> bool:
    """
    Sauvegarde les données financières d'un utilisateur.
    Retourne True si succès, False sinon.
    """
    try:
        file = _get_user_file(user_id)
        data["updated_at"] = datetime.now().isoformat()
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Storage Error] {e}")
        return False


def add_transaction(user_id: str, transaction: dict) -> bool:
    """
    Ajoute une transaction (dépense ou revenu) au profil utilisateur.

    transaction = {
        "type": "depense" | "revenu",
        "montant": float,
        "categorie": str,
        "description": str,
        "date": str (ISO),
        "source": "cash" | "mtn" | "moov" | "banque"
    }
    """
    data = load_user_data(user_id)
    transaction["id"] = f"tx_{datetime.now().timestamp()}"
    transaction.setdefault("date", datetime.now().isoformat())
    data["transactions"].append(transaction)
    return save_user_data(user_id, data)


def get_transactions(user_id: str, month: str = None) -> list:
    """
    Récupère les transactions d'un utilisateur.
    Si month est fourni (format YYYY-MM), filtre par mois.
    """
    data = load_user_data(user_id)
    transactions = data.get("transactions", [])
    if month:
        transactions = [
            t for t in transactions
            if t.get("date", "").startswith(month)
        ]
    return transactions


def get_summary(user_id: str, month: str = None) -> dict:
    """
    Calcule un résumé financier : total revenus, dépenses, solde.
    """
    transactions = get_transactions(user_id, month)
    revenus = sum(t["montant"] for t in transactions if t["type"] == "revenu")
    depenses = sum(t["montant"] for t in transactions if t["type"] == "depense")
    return {
        "revenus": revenus,
        "depenses": depenses,
        "solde": revenus - depenses,
        "nb_transactions": len(transactions),
        "month": month or "all",
    }