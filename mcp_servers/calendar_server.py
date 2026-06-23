"""
PocketSage - MCP Calendar Server
Gère les événements financiers prévisibles : loyers, tontines, fêtes.
Adapté au calendrier des dépenses sociales d'Afrique de l'Ouest.
"""

import json
from datetime import datetime, date
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("pocketsage-calendar")

# Événements financiers récurrents typiques en Afrique de l'Ouest
RECURRING_EVENTS = [
    {
        "day_of_month": 1,
        "name": "Loyer",
        "categorie": "logement",
        "type": "depense",
        "description": "Paiement du loyer mensuel",
        "priority": "haute",
    },
    {
        "day_of_month": 5,
        "name": "Electricité / Eau",
        "categorie": "logement",
        "type": "depense",
        "description": "Factures SBEE / SONEB",
        "priority": "haute",
    },
    {
        "day_of_month": 15,
        "name": "Tontine",
        "categorie": "social",
        "type": "depense",
        "description": "Cotisation tontine mensuelle",
        "priority": "moyenne",
    },
    {
        "day_of_month": 28,
        "name": "Courses fin de mois",
        "categorie": "alimentation",
        "type": "depense",
        "description": "Approvisionnement mensuel marché",
        "priority": "haute",
    },
]

# Fêtes et événements culturels importants (Bénin / Afrique de l'Ouest)
CULTURAL_EVENTS_2026 = [
    {"date": "2026-01-01", "name": "Nouvel An", "impact": "Dépenses festives élevées"},
    {"date": "2026-03-20", "name": "Fête du Vodoun", "impact": "Cérémonies et offrandes"},
    {"date": "2026-04-05", "name": "Pâques", "impact": "Dépenses familiales"},
    {"date": "2026-06-01", "name": "Fête des Mères (approx)", "impact": "Cadeaux famille"},
    {"date": "2026-08-01", "name": "Fête Nationale du Bénin", "impact": "Célébrations"},
    {"date": "2026-12-25", "name": "Noël", "impact": "Dépenses festives très élevées"},
    {"date": "2026-12-31", "name": "Réveillon", "impact": "Dépenses festives élevées"},
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_upcoming_expenses",
            description=(
                "Retourne les dépenses financières prévisibles dans les N prochains jours. "
                "Inclut loyer, tontines, factures, fêtes culturelles."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Nombre de jours à anticiper (défaut: 15)",
                        "default": 15,
                    },
                    "user_tontines": {
                        "type": "array",
                        "description": "Tontines personnalisées de l'utilisateur",
                        "items": {"type": "object"},
                    },
                },
            },
        ),
        Tool(
            name="get_month_events",
            description="Retourne tous les événements financiers du mois en cours.",
            inputSchema={
                "type": "object",
                "properties": {
                    "month": {
                        "type": "string",
                        "description": "Mois au format YYYY-MM (défaut: mois actuel)",
                    },
                },
            },
        ),
        Tool(
            name="add_custom_event",
            description="Ajoute un événement financier personnalisé au calendrier.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "date": {"type": "string", "description": "Format YYYY-MM-DD"},
                    "montant_estime": {"type": "number"},
                    "categorie": {"type": "string"},
                    "recurrent": {"type": "boolean"},
                },
                "required": ["name", "date"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:

    today = date.today()

    if name == "get_upcoming_expenses":
        days_ahead = arguments.get("days_ahead", 15)
        user_tontines = arguments.get("user_tontines", [])
        upcoming = []

        # Vérifier les événements récurrents
        for event in RECURRING_EVENTS:
            event_day = event["day_of_month"]
            # Calculer la prochaine occurrence
            if today.day <= event_day:
                event_date = today.replace(day=event_day)
            else:
                # Mois prochain
                if today.month == 12:
                    event_date = today.replace(year=today.year + 1, month=1, day=event_day)
                else:
                    event_date = today.replace(month=today.month + 1, day=event_day)

            days_until = (event_date - today).days
            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    **event,
                    "date": event_date.isoformat(),
                    "days_until": days_until,
                })

        # Ajouter les tontines personnalisées
        for tontine in user_tontines:
            upcoming.append({
                "name": tontine.get("name", "Tontine"),
                "type": "depense",
                "categorie": "social",
                "days_until": tontine.get("days_until", 0),
                "priority": "haute",
            })

        # Vérifier les fêtes culturelles
        for cultural in CULTURAL_EVENTS_2026:
            event_date = date.fromisoformat(cultural["date"])
            days_until = (event_date - today).days
            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    "name": cultural["name"],
                    "type": "depense",
                    "categorie": "social",
                    "description": cultural["impact"],
                    "date": cultural["date"],
                    "days_until": days_until,
                    "priority": "moyenne",
                })

        # Trier par proximité
        upcoming.sort(key=lambda x: x.get("days_until", 999))

        result = {
            "today": today.isoformat(),
            "days_ahead": days_ahead,
            "upcoming_count": len(upcoming),
            "events": upcoming,
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    elif name == "get_month_events":
        month_str = arguments.get("month", today.strftime("%Y-%m"))
        year, month = map(int, month_str.split("-"))

        events = []
        for event in RECURRING_EVENTS:
            events.append({
                **event,
                "date": f"{month_str}-{event['day_of_month']:02d}",
            })

        result = {
            "month": month_str,
            "events": events,
            "total_events": len(events),
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    elif name == "add_custom_event":
        # Dans une vraie app, on sauvegarderait en base
        # Ici on confirme juste la réception
        result = {
            "status": "success",
            "message": f"Événement '{arguments.get('name')}' ajouté au calendrier",
            "event": arguments,
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    return [TextContent(type="text", text=json.dumps({"error": f"Outil '{name}' inconnu"}))]


async def main():
    """Point d'entrée du serveur MCP Calendar."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())