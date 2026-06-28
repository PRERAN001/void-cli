import os

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pyfiglet import Figlet

console = Console()


def print_banner():
    console.clear()

    figlet = Figlet(font="ansi_shadow")
    banner = figlet.renderText("VOIDCLI")
    console.print(f"[bold #7c6af7]{banner}[/]", end="")
    console.print("[dim]  ai-powered code intelligence - v1.0.0[/]\n")

    llm_status = "connected" if os.getenv("OPENROUTER_API_KEY") else "missing key"
    llm_style = "bold #4caf50" if os.getenv("OPENROUTER_API_KEY") else "bold #e0a020"

    statuses = [
        Text(f"  * LLM {llm_status}   ", style=llm_style),
        Text("  * GitHub: not linked   ", style="bold #e0a020"),
        Text("  * Repo detected  ", style="bold #4caf50"),
    ]
    console.print(Columns(statuses))
    console.print()
    console.rule(style="#2a2a2e")
    console.print()


def run_prompt(prompt: str, gateway, orchestrator):
    gateway.receive(prompt)
    orchestrator.run()


def ask_assistant(prompt: str, session):
    try:
        answer = session.llm.generate(
            prompt=prompt,
            system_prompt=(
                "You are a helpful developer assistant. Answer direct questions plainly. "
                "If the user asks for coding work, explain that Agentic Works is better for project changes."
            ),
        )
        console.print(Panel(
            answer,
            border_style="#7c6af7",
            title="[bold #7c6af7]assistant[/]",
            title_align="left",
            padding=(1, 2),
        ))
    except Exception as exc:
        console.print(Panel(
            str(exc),
            border_style="#e05a5a",
            title="[bold #e05a5a]assistant error[/]",
            title_align="left",
            padding=(1, 2),
        ))


def ask_for_input(session, gateway, orchestrator):
    import questionary

    from .questions import (
        STYLE,
        agentic_works,
        analyze_repository,
        integrations_menu,
        review_code,
        search_file,
    )

    while True:
        choice = questionary.select(
            "  What would you like to do?",
            choices=[
                questionary.Choice("Analyze Repository", value="analyze"),
                questionary.Choice("Review Code", value="review"),
                questionary.Choice("Search for a File", value="search"),
                questionary.Choice("Integrations", value="integrations"),
                questionary.Choice("Agentic Works", value="agentic"),
                questionary.Choice("Ask Assistant", value="ask"),
                questionary.Separator(),
                questionary.Choice("Exit", value="exit"),
            ],
            style=STYLE,
            instruction=" (arrows, enter to select)",
        ).ask()

        if choice == "analyze":
            analyze_repository(console)
        elif choice == "review":
            review_code(console)
        elif choice == "search":
            search_file(console)
        elif choice == "integrations":
            integrations_menu(console)
        elif choice == "agentic":
            agentic_works(console, gateway, orchestrator)
        elif choice == "ask":
            prompt = questionary.text("  What should I work on?", style=STYLE).ask()
            if prompt:
                ask_assistant(prompt, session)
        elif choice == "exit" or choice is None:
            console.print()
            console.rule(style="#3a3a3a")
            console.print("[dim #7c6af7]  goodbye - voidcli v1.0.0[/]\n")
            break


if __name__ == "__main__":
    from main import build_app

    app_session, app_gateway, app_orchestrator = build_app()
    print_banner()
    ask_for_input(app_session, app_gateway, app_orchestrator)
