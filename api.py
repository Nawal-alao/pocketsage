"""
PocketSage - API FastAPI
Serveur REST qui connecte le dashboard web aux agents.
Point d'entrée unique pour toutes les requêtes frontend.
"""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agents import OrchestratorAgent
from tools.storage import get_summary, get_transactions, load_user_data

load_dotenv()

# ── APP ──
app = FastAPI(
    title="PocketSage API",
    description="Assistant financier personnel pour l'Afrique de l'Ouest",
    version="1.0.0",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── STATIC FILES ──
app.mount("/", StaticFiles(directory="web", html=True), name="static")

# ── ORCHESTRATOR (singleton) ──
orchestrator = OrchestratorAgent()


# ── SCHEMAS ──
class ChatRequest(BaseModel):
    user_id: str
    message: str
    lang: str = "fr"


class TransactionRequest(BaseModel):
    user_id: str
    type: str           # depense | revenu
    montant: float
    categorie: str
    description: str = ""
    source: str = "cash"  # cash | mtn | moov | banque


# ── ROUTES ──

@app.get("/")
async def root():
    """Sert le dashboard web."""
    return FileResponse("web/index.html")


@app.get("/health")
async def health():
    """Vérifie que l'API tourne."""
    return {
        "status": "ok",
        "app": "PocketSage",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Point d'entrée principal du chat.
    Reçoit un message, le route vers le bon agent, retourne la réponse.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message vide")

    result = orchestrator.process(req.user_id, req.message)
    return result


@app.get("/summary/{user_id}")
async def get_user_summary(user_id: str, month: str = None):
    """
    Retourne le résumé financier d'un utilisateur.
    Optionnel : filtrer par mois (format YYYY-MM).
    """
    if not month:
        month = datetime.now().strftime("%Y-%m")
    summary = get_summary(user_id, month)
    return summary


@app.get("/transactions/{user_id}")
async def get_user_transactions(
    user_id: str,
    month: str = None,
    limit: int = 50,
):
    """
    Retourne les transactions d'un utilisateur.
    Optionnel : filtrer par mois, limiter le nombre de résultats.
    """
    transactions = get_transactions(user_id, month)
    return {
        "user_id": user_id,
        "month": month,
        "total": len(transactions),
        "transactions": transactions[-limit:],
    }


@app.get("/alerts/{user_id}")
async def get_user_alerts(user_id: str, lang: str = "fr"):
    """
    Retourne les alertes financières d'un utilisateur.
    Analyse la situation du mois en cours et projette la fin de mois.
    """
    from agents.alert_agent import AlertAgent
    alert_agent = AlertAgent()
    alerts = alert_agent.check_alerts(user_id, lang)
    return alerts


@app.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Retourne le profil d'un utilisateur."""
    data = load_user_data(user_id)
    return {
        "user_id": user_id,
        "profile": data.get("profile", {}),
        "created_at": data.get("created_at"),
        "tontines": data.get("tontines", []),
    }


@app.post("/transaction")
async def add_manual_transaction(req: TransactionRequest):
    """
    Ajoute une transaction manuellement (sans passer par le chat).
    Utile pour les tests et l'import de données.
    """
    from tools.storage import add_transaction
    transaction = {
        "type": req.type,
        "montant": req.montant,
        "categorie": req.categorie,
        "description": req.description,
        "source": req.source,
        "date": datetime.now().isoformat(),
    }
    success = add_transaction(req.user_id, transaction)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement")
    return {"status": "success", "transaction": transaction}


@app.get("/insight/{user_id}")
async def get_insight(user_id: str, month: str = None, lang: str = "fr"):
    """
    Génère une analyse financière personnalisée pour l'utilisateur.
    """
    from agents.insight_agent import InsightAgent
    insight_agent = InsightAgent()
    analysis = insight_agent.analyze(user_id, month, lang)
    return {"user_id": user_id, "analysis": analysis}


@app.post("/decision")
async def analyze_decision(
    user_id: str,
    question: str,
    lang: str = "fr"
):
    """
    Analyse une décision financière complexe avec Antigravity.
    Retourne plusieurs scénarios et une recommandation.
    """
    from agents.antigravity_agent import AntigravityAgent
    agent = AntigravityAgent()
    result = agent.analyze_decision(user_id, question, lang)
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )