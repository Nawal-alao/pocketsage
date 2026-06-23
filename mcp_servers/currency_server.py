"""
PocketSage - MCP Currency Server
Fournit les taux de change en temps réel pour le FCFA.
MCP = Model Context Protocol — permet à l'agent d'accéder à des données externes.
"""

import json
import httpx
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialisation du serveur MCP
app = Server("pocketsage-currency")

# Taux de fallback si l'API est indisponible (taux approximatifs)
FALLBACK_RATES = {
    "EUR": 655.957,   # 1 EUR = 655.957 FCFA (taux fixe historique)
    "USD": 600.0,
    "GBP": 750.0,
    "NGN": 0.38,      # Naira nigérian
    "GHS": 45.0,      # Cedi ghanéen
    "XOF": 1.0,       # FCFA lui-même
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Liste les outils disponibles sur ce serveur MCP."""
    return [
        Tool(
            name="get_exchange_rate",
            description=(
                "Obtenir le taux de change entre le FCFA et une autre devise. "
                "Utile pour convertir des montants en EUR, USD, NGN, GHS, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "Code devise cible (EUR, USD, GBP, NGN, GHS)",
                    },
                    "amount_fcfa": {
                        "type": "number",
                        "description": "Montant en FCFA à convertir",
                    },
                },
                "required": ["currency"],
            },
        ),
        Tool(
            name="get_all_rates",
            description="Obtenir tous les taux de change disponibles pour le FCFA.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="convert_to_fcfa",
            description="Convertir un montant d'une devise étrangère vers le FCFA.",
            inputSchema={
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "Code devise source (EUR, USD, etc.)",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Montant dans la devise source",
                    },
                },
                "required": ["currency", "amount"],
            },
        ),
    ]


async def _fetch_live_rates() -> dict:
    """
    Tente de récupérer les taux en temps réel.
    Retourne les taux de fallback si l'API est indisponible.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # API gratuite sans clé requise
            response = await client.get(
                "https://api.exchangerate-api.com/v4/latest/XOF"
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("rates", FALLBACK_RATES)
    except Exception:
        pass
    return FALLBACK_RATES


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatcher des outils MCP."""

    if name == "get_exchange_rate":
        currency = arguments.get("currency", "EUR").upper()
        amount_fcfa = arguments.get("amount_fcfa", 1000)

        rates = await _fetch_live_rates()
        rate = rates.get(currency)

        if not rate:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Devise '{currency}' non disponible",
                    "available": list(rates.keys()),
                }, ensure_ascii=False)
            )]

        # FCFA → devise cible
        converted = amount_fcfa / rate if currency != "XOF" else amount_fcfa

        result = {
            "from": "FCFA",
            "to": currency,
            "rate": rate,
            "amount_fcfa": amount_fcfa,
            "converted": round(converted, 2),
            "timestamp": datetime.now().isoformat(),
            "source": "live" if rates != FALLBACK_RATES else "fallback",
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    elif name == "get_all_rates":
        rates = await _fetch_live_rates()
        result = {
            "base": "XOF (FCFA)",
            "rates": {k: v for k, v in rates.items()
                      if k in ["EUR", "USD", "GBP", "NGN", "GHS", "MAD", "XAF"]},
            "timestamp": datetime.now().isoformat(),
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    elif name == "convert_to_fcfa":
        currency = arguments.get("currency", "EUR").upper()
        amount = arguments.get("amount", 1)

        rates = await _fetch_live_rates()
        rate = rates.get(currency)

        if not rate:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Devise '{currency}' non disponible"})
            )]

        amount_fcfa = amount * rate
        result = {
            "from": currency,
            "to": "FCFA",
            "original_amount": amount,
            "amount_fcfa": round(amount_fcfa, 0),
            "rate": rate,
            "timestamp": datetime.now().isoformat(),
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    return [TextContent(type="text", text=json.dumps({"error": f"Outil '{name}' inconnu"}))]


async def main():
    """Point d'entrée du serveur MCP Currency."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())