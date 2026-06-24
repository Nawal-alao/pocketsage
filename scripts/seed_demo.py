"""
PocketSage - Script de données de démo
Génère des transactions réalistes pour la démonstration vidéo.
Simule 30 jours de vie financière d'un commerçant béninois.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from tools.storage import add_transaction, save_user_data, load_user_data
from rich.console import Console
from rich.progress import track

console = Console()
USER_ID = "user_demo"


def seed_demo_data():
    """Génère 30 jours de données financières réalistes."""

    console.print("\n[bold cyan]💰 PocketSage — Génération données démo[/bold cyan]\n")

    # Réinitialiser le profil demo
    data = load_user_data(USER_ID)
    data["transactions"] = []
    data["profile"] = {
        "language": "fr",
        "currency": "CFA",
        "income_type": "variable",
        "name": "Kofi Demo",
        "activity": "Commerce de textile",
    }
    data["tontines"] = [
        {
            "name": "Tontine Marché Central",
            "montant_mensuel": 10000,
            "jour": 15,
            "membres": 12,
        }
    ]
    save_user_data(USER_ID, data)

    today = datetime.now()
    start_date = today - timedelta(days=30)

    # Transactions réalistes d'un commerçant béninois
    transactions = [

        # SEMAINE 1
        {"jour": 1, "type": "revenu", "montant": 45000,
         "categorie": "commerce", "description": "Vente tissus lundi",
         "source": "cash"},
        {"jour": 1, "type": "depense", "montant": 2500,
         "categorie": "alimentation", "description": "Marché matin",
         "source": "cash"},
        {"jour": 1, "type": "depense", "montant": 500,
         "categorie": "transport", "description": "Zémidjan aller",
         "source": "cash"},
        {"jour": 2, "type": "depense", "montant": 1500,
         "categorie": "alimentation", "description": "Repas midi boutique",
         "source": "cash"},
        {"jour": 3, "type": "revenu", "montant": 28000,
         "categorie": "commerce", "description": "Vente mercredi",
         "source": "cash"},
        {"jour": 3, "type": "depense", "montant": 5000,
         "categorie": "transport", "description": "Livraison commande",
         "source": "moov"},
        {"jour": 4, "type": "depense", "montant": 3000,
         "categorie": "alimentation", "description": "Courses famille",
         "source": "cash"},
        {"jour": 5, "type": "revenu", "montant": 52000,
         "categorie": "commerce", "description": "Grosse vente vendredi",
         "source": "mtn"},
        {"jour": 5, "type": "depense", "montant": 15000,
         "categorie": "logement", "description": "Avance loyer",
         "source": "cash"},
        {"jour": 7, "type": "depense", "montant": 8000,
         "categorie": "alimentation", "description": "Courses weekend famille",
         "source": "cash"},

        # SEMAINE 2
        {"jour": 8, "type": "revenu", "montant": 35000,
         "categorie": "commerce", "description": "Vente lundi",
         "source": "cash"},
        {"jour": 8, "type": "depense", "montant": 2000,
         "categorie": "transport", "description": "Transport marchandise",
         "source": "cash"},
        {"jour": 9, "type": "depense", "montant": 12000,
         "categorie": "sante", "description": "Consultation médecin enfant",
         "source": "moov"},
        {"jour": 10, "type": "revenu", "montant": 18000,
         "categorie": "commerce", "description": "Vente mercredi",
         "source": "cash"},
        {"jour": 11, "type": "depense", "montant": 3500,
         "categorie": "alimentation", "description": "Marché jeudi",
         "source": "cash"},
        {"jour": 12, "type": "revenu", "montant": 41000,
         "categorie": "commerce", "description": "Vente vendredi",
         "source": "mtn"},
        {"jour": 12, "type": "depense", "montant": 20000,
         "categorie": "commerce", "description": "Achat nouveau stock tissu",
         "source": "cash"},
        {"jour": 14, "type": "depense", "montant": 5000,
         "categorie": "social", "description": "Contribution baptême voisin",
         "source": "cash"},

        # SEMAINE 3
        {"jour": 15, "type": "depense", "montant": 10000,
         "categorie": "social", "description": "Cotisation tontine mensuelle",
         "source": "mtn"},
        {"jour": 15, "type": "revenu", "montant": 29000,
         "categorie": "commerce", "description": "Vente lundi",
         "source": "cash"},
        {"jour": 16, "type": "depense", "montant": 4500,
         "categorie": "alimentation", "description": "Repas famille",
         "source": "cash"},
        {"jour": 17, "type": "revenu", "montant": 15000,
         "categorie": "freelance", "description": "Prestation couture",
         "source": "moov"},
        {"jour": 18, "type": "depense", "montant": 2500,
         "categorie": "education", "description": "Fournitures école enfant",
         "source": "cash"},
        {"jour": 19, "type": "revenu", "montant": 48000,
         "categorie": "commerce", "description": "Grosse commande vendredi",
         "source": "mtn"},
        {"jour": 19, "type": "depense", "montant": 6000,
         "categorie": "alimentation", "description": "Courses weekend",
         "source": "cash"},
        {"jour": 21, "type": "depense", "montant": 35000,
         "categorie": "logement", "description": "Loyer mois complet",
         "source": "cash"},

        # SEMAINE 4
        {"jour": 22, "type": "revenu", "montant": 22000,
         "categorie": "commerce", "description": "Vente lundi",
         "source": "cash"},
        {"jour": 23, "type": "depense", "montant": 3000,
         "categorie": "transport", "description": "Carburant zémidjan",
         "source": "cash"},
        {"jour": 24, "type": "revenu", "montant": 31000,
         "categorie": "commerce", "description": "Vente mercredi",
         "source": "cash"},
        {"jour": 25, "type": "depense", "montant": 8500,
         "categorie": "alimentation", "description": "Provisions fin de mois",
         "source": "cash"},
        {"jour": 26, "type": "revenu", "montant": 38000,
         "categorie": "commerce", "description": "Vente vendredi",
         "source": "mtn"},
        {"jour": 26, "type": "depense", "montant": 4000,
         "categorie": "logement", "description": "Facture SBEE électricité",
         "source": "moov"},
        {"jour": 27, "type": "depense", "montant": 2000,
         "categorie": "logement", "description": "Facture SONEB eau",
         "source": "moov"},
        {"jour": 28, "type": "depense", "montant": 7000,
         "categorie": "social", "description": "Aide famille proche",
         "source": "mtn"},
        {"jour": 29, "type": "revenu", "montant": 19000,
         "categorie": "commerce", "description": "Vente dimanche marché",
         "source": "cash"},
        {"jour": 30, "type": "depense", "montant": 1500,
         "categorie": "autre", "description": "Credit téléphone",
         "source": "moov"},
    ]

    # Insérer les transactions avec les bonnes dates
    for tx in track(transactions, description="Génération des transactions..."):
        tx_date = start_date + timedelta(days=tx["jour"] - 1)
        transaction = {
            "type": tx["type"],
            "montant": tx["montant"],
            "categorie": tx["categorie"],
            "description": tx["description"],
            "source": tx["source"],
            "date": tx_date.isoformat(),
        }
        add_transaction(USER_ID, transaction)

    # Afficher le résumé
    from tools.storage import get_summary
    summary = get_summary(USER_ID)

    console.print("\n[bold green]✅ Données démo générées avec succès ![/bold green]\n")
    console.print(f"[cyan]Total revenus :[/cyan]      {summary['revenus']:,.0f} FCFA")
    console.print(f"[red]Total dépenses :[/red]     {summary['depenses']:,.0f} FCFA")
    console.print(f"[bold]Solde final :[/bold]        {summary['solde']:,.0f} FCFA")
    console.print(f"[dim]Transactions :[/dim]       {summary['nb_transactions']}")
    console.print("\n[dim]Lance 'python api.py' et ouvre http://localhost:8000[/dim]\n")


if __name__ == "__main__":
    seed_demo_data()