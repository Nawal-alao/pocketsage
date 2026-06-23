"""
PocketSage - Point d'entrée principal
Lance l'interface CLI pour tester les agents localement.
"""
import time
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from agents import OrchestratorAgent

load_dotenv()
console = Console()

ALERT_COLORS = {
    "green": "bold green",
    "yellow": "bold yellow",
    "red": "bold red",
}

ALERT_ICONS = {
    "green": "🟢",
    "yellow": "🟡",
    "red": "🔴",
}


def print_welcome():
    console.print(Panel.fit(
        "[bold cyan]💰 PocketSage[/bold cyan]\n"
        "[dim]Ton assistant financier personnel — Afrique de l'Ouest[/dim]\n"
        "[dim]Français • English • Fon • Yoruba[/dim]",
        border_style="cyan"
    ))


def print_response(result: dict):
    """Affiche la réponse de l'agent avec mise en forme."""
    intent = result.get("intent", "general")
    agent = result.get("agent_used", "")
    response = result.get("response", "")
    data = result.get("data") or {}

    # Badge agent utilisé
    agent_colors = {
        "BudgetAgent": "green",
        "InsightAgent": "blue",
        "AlertAgent": "yellow",
        "Orchestrator": "cyan",
    }
    color = agent_colors.get(agent, "white")
    console.print(f"\n[dim]→ [{color}]{agent}[/{color}][/dim]")

    # Alerte niveau si AlertAgent
    if intent == "alert" and "alert_level" in data:
        level = data["alert_level"]
        icon = ALERT_ICONS.get(level, "🟢")
        style = ALERT_COLORS.get(level, "white")
        console.print(f"[{style}]{icon} Niveau : {level.upper()}[/{style}]")

    # Réponse principale
    console.print(Panel(
        Markdown(response),
        border_style=color,
        padding=(1, 2),
    ))

    # Transaction sauvegardée
    if data.get("transaction_saved"):
        tx = data.get("transaction", {})
        console.print(
            f"[bold green]✅ Transaction enregistrée :[/bold green] "
            f"{tx.get('type', '').upper()} • "
            f"{tx.get('montant', 0):,.0f} FCFA • "
            f"{tx.get('categorie', '')} • "
            f"{tx.get('source', '')}"
        )

    # Actions recommandées si alerte
    actions = data.get("actions", [])
    if actions:
        console.print("[bold]Actions recommandées :[/bold]")
        for i, action in enumerate(actions, 1):
            console.print(f"  {i}. {action}")


def select_language() -> str:
    """Demande la langue préférée à l'utilisateur."""
    console.print("\n[bold]Choisis ta langue / Choose your language :[/bold]")
    console.print("  [cyan]1[/cyan] → Français")
    console.print("  [cyan]2[/cyan] → English")
    console.print("  [cyan]3[/cyan] → Fon")
    console.print("  [cyan]4[/cyan] → Yoruba")

    choice = Prompt.ask("\nTon choix", choices=["1", "2", "3", "4"], default="1")
    lang_map = {"1": "fr", "2": "en", "3": "fon", "4": "yo"}
    return lang_map[choice]


def main():
    """Boucle principale CLI."""
    print_welcome()

    # Sélection langue
    lang = select_language()

    # ID utilisateur simple pour les tests
    user_id = "user_demo"

    # Initialiser l'orchestrator
    orchestrator = OrchestratorAgent()

    # Message de bienvenue
    welcome = orchestrator.welcome(user_id, lang)
    console.print(Panel(
        Markdown(welcome),
        border_style="cyan",
        padding=(1, 2),
    ))

    # Boucle de conversation
    console.print("\n[dim]Tape 'quitter' ou 'exit' pour arrêter.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]Toi[/bold cyan]")

            if user_input.lower() in ["quitter", "exit", "quit", "q"]:
                console.print("\n[bold cyan]À bientôt ! Bonne gestion ! 💰[/bold cyan]")
                break

            if not user_input.strip():
                continue

            # Traiter le message
            with console.status("[dim]PocketSage réfléchit...[/dim]"):
                time.sleep(1)  # Respecter le rate limit free tier
                result = orchestrator.process(user_id, user_input)

            print_response(result)

        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]À bientôt ! 💰[/bold cyan]")
            break
        except Exception as e:
            console.print(f"[red]Erreur : {e}[/red]")


if __name__ == "__main__":
    main()