from voidcli.core.gateway import Gateway
from voidcli.core.orchestrator import Orchestrator
from voidcli.core.registry import Registry
from voidcli.core.session import Session


def build_app():
    session = Session()

    registry = Registry(session)
    registry.register_default_agents()
    registry.register_default_tools()
    session.registry = registry

    gateway = Gateway(session)
    orchestrator = Orchestrator(session)

    return session, gateway, orchestrator


def run_prompt(prompt: str, gateway: Gateway, orchestrator: Orchestrator):
    gateway.receive(prompt)
    orchestrator.run()


def main():
    session, gateway, orchestrator = build_app()

    try:
        from voidcli.ui.ui import ask_for_input, print_banner

        print_banner()
        ask_for_input(
            session=session,
            gateway=gateway,
            orchestrator=orchestrator,
        )
    except ModuleNotFoundError as exc:
        if exc.name not in {"rich", "questionary", "pyfiglet"}:
            raise

        print("\nReady\n")
        while True:
            prompt = input("> ").strip()

            if prompt.lower() in ("exit", "quit"):
                break

            if prompt:
                run_prompt(prompt, gateway, orchestrator)


if __name__ == "__main__":
    main()
