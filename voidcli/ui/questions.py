import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import questionary
from dotenv import load_dotenv
from questionary import Style
from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


STYLE = Style([
    ("qmark", "fg:#7c6af7 bold"),
    ("question", "fg:#cccccc bold"),
    ("answer", "fg:#7c6af7 bold"),
    ("pointer", "fg:#7c6af7 bold"),
    ("highlighted", "fg:#c4b5fd bold"),
    ("selected", "fg:#7c6af7"),
    ("separator", "fg:#3a3a3a"),
    ("instruction", "fg:#555555 italic"),
])


SENSITIVE_ENV_MARKERS = ("TOKEN", "KEY", "SECRET", "PASSWORD", "URI")


def section_header(console: Console, title: str, icon: str = "*"):
    console.print()
    console.rule(f"[bold #7c6af7]{icon}  {title}[/]", style="#3a3a3a")
    console.print()


def success(console: Console, msg: str):
    console.print(f"[bold #4caf50]  OK  {msg}[/]")


def warn(console: Console, msg: str):
    console.print(f"[bold #e0a020]  WARN  {msg}[/]")


def error(console: Console, msg: str):
    console.print(f"[bold #e05a5a]  ERROR  {msg}[/]")


def info(console: Console, msg: str):
    console.print(f"[dim #7c6af7]  >  {msg}[/]")


def pause(console: Console):
    console.print()
    console.input("[dim]  press enter to continue...[/]")


def spinning(console: Console, label: str, seconds: float = 1.0):
    with Live(console=console, refresh_per_second=12) as live:
        for _ in range(int(seconds * 12)):
            live.update(Text(f"  ...  {label}", style="#7c6af7"))
            time.sleep(1 / 12)


def _env_path() -> Path:
    return Path.cwd() / ".env"


def _is_sensitive_env(name: str) -> bool:
    return any(marker in name.upper() for marker in SENSITIVE_ENV_MARKERS)


def _read_env_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def _write_env_values(values: dict[str, str]):
    path = _env_path()
    lines = _read_env_lines(path)
    seen = set()
    updated_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            updated_lines.append(line)
            continue

        key = line.split("=", 1)[0].strip()
        if key in values:
            updated_lines.append(f"{key}={values[key]}")
            seen.add(key)
        else:
            updated_lines.append(line)

    for key, value in values.items():
        if key not in seen:
            updated_lines.append(f"{key}={value}")

    path.write_text("\n".join(updated_lines).rstrip() + "\n", encoding="utf-8")

    for key, value in values.items():
        os.environ[key] = value

    load_dotenv(path, override=True)


def _find_git_root(start_path: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", start_path, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _looks_like_git_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "ssh", "git"} or value.startswith("git@")


def _repo_folder_name(repo_url: str) -> str:
    name = repo_url.rstrip("/").rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in name)
    return safe or "repo"


def _clone_repo(console: Console, repo_url: str) -> str | None:
    clone_root = Path.cwd() / ".voidcli" / "repos"
    clone_root.mkdir(parents=True, exist_ok=True)

    target = clone_root / _repo_folder_name(repo_url)
    if target.exists():
        update = questionary.confirm(
            f"  Repo already exists at {target}. Pull latest changes?",
            default=True,
            style=STYLE,
        ).ask()
        if update:
            result = subprocess.run(
                ["git", "-C", str(target), "pull", "--ff-only"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                error(console, result.stderr.strip() or "git pull failed.")
                return None
        return str(target)

    spinning(console, "Cloning repository...")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error(console, result.stderr.strip() or "git clone failed.")
        return None
    return str(target)


def ask_for_repository(console: Console) -> str | None:
    source = questionary.text(
        "  Enter Git repo link or local repo path:",
        default=os.getcwd(),
        style=STYLE,
    ).ask()

    if not source:
        return None

    source = source.strip().strip('"')

    if _looks_like_git_url(source):
        return _clone_repo(console, source)

    path = os.path.abspath(os.path.expanduser(source))
    if not os.path.exists(path):
        error(console, "That path does not exist.")
        return None

    repo_root = _find_git_root(path)
    if repo_root is None:
        error(console, "That path is not inside a Git repository.")
        return None

    return repo_root


def analyze_repository(console: Console):
    section_header(console, "Analyze Repository")

    repo_root = ask_for_repository(console)
    if repo_root is None:
        pause(console)
        return

    spinning(console, "Scanning repository structure...")

    file_count = 0
    ext_counter = Counter()
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fname in filenames:
            file_count += 1
            ext = os.path.splitext(fname)[1].lower() or "<no ext>"
            ext_counter[ext] += 1
            try:
                total_size += os.path.getsize(os.path.join(dirpath, fname))
            except OSError:
                pass

    top_exts = "\n".join(f"  {ext:<10} {count}" for ext, count in ext_counter.most_common(5))
    summary = (
        f"[bold]Repository:[/] {repo_root}\n"
        f"[bold]Total files:[/] {file_count}\n"
        f"[bold]Total size:[/] {total_size / (1024 * 1024):.2f} MB\n\n"
        f"[bold]Top file types:[/]\n{top_exts}"
    )

    console.print(Panel(
        summary,
        border_style="#3a3a3a",
        title="[#7c6af7]repository analysis[/]",
        title_align="left",
    ))
    pause(console)


def review_code(console: Console):
    section_header(console, "Review Code")

    source = questionary.select(
        "How would you like to provide the code?",
        choices=[
            questionary.Choice("From a file path", value="file"),
            questionary.Choice("Paste code manually", value="paste"),
            questionary.Choice("Back", value="back"),
        ],
        style=STYLE,
    ).ask()

    if source == "back" or source is None:
        return

    code = ""
    lang = "text"

    if source == "file":
        path = questionary.path("  Enter file path:", style=STYLE).ask()
        if not path or not os.path.isfile(path):
            error(console, "File not found.")
            pause(console)
            return
        with open(path, "r", errors="ignore", encoding="utf-8") as handle:
            code = handle.read()
        lang = path.rsplit(".", 1)[-1] if "." in path else "text"
        console.print()
        console.print(Syntax(code[:2000], lang, theme="monokai", line_numbers=True))
        if len(code) > 2000:
            info(console, f"Showing first 2000 of {len(code)} chars")

    elif source == "paste":
        console.print("[dim]  Paste your code below. Type [bold]END[/bold] on a new line when done.[/]\n")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        code = "\n".join(lines)

    if not code.strip():
        warn(console, "No code provided.")
        pause(console)
        return

    spinning(console, "Sending to LLM for review...")

    review_prompt = f"""Review the following code.
Provide:
1. Bugs
2. Security Issues
3. Performance Issues
4. Code Quality Issues
5. Suggestions

Code:
{code}
"""
    try:
        from voidcli.services.llmcall import LLMClient

        llm = LLMClient()
        result = llm.generate(
            prompt=review_prompt,
            system_prompt=(
                "You are a senior software engineer performing code reviews. "
                "Be direct and concise. Focus on real issues and actionable improvements."
            ),
        )
        console.print(Panel(
            result,
            border_style="#7c6af7",
            title="[bold #7c6af7]code review[/]",
            title_align="left",
            padding=(1, 2),
        ))
    except Exception as exc:
        error(console, f"LLM call failed: {exc}")

    pause(console)


def search_file(console: Console):
    section_header(console, "Search for a File")

    path = questionary.path("  Enter directory path:", style=STYLE).ask()
    if not path:
        error(console, "Path cannot be empty.")
        pause(console)
        return
    if not os.path.exists(path):
        error(console, "Path does not exist.")
        pause(console)
        return

    filename = questionary.text("  File name to search:", style=STYLE).ask()
    if not filename:
        error(console, "File name cannot be empty.")
        pause(console)
        return

    spinning(console, f"Searching for '{filename}'...")

    matches = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if filename.lower() in file.lower():
                matches.append(os.path.join(root, file))

    if not matches:
        warn(console, "No matching files found.")
        pause(console)
        return

    success(console, f"Found {len(matches)} match(es)")
    selected = questionary.select(
        "  Select a file:",
        choices=matches + [questionary.Separator(), "Back"],
        style=STYLE,
    ).ask()

    if selected == "Back" or selected is None:
        return

    console.print(Panel(
        f"[bold #c4b5fd]{selected}[/]",
        title="[#7c6af7]selected file[/]",
        title_align="left",
        border_style="#3a3a3a",
    ))
    pause(console)


def show_connected_services(console: Console):
    from voidcli.services.integrations import IntegrationManager

    section_header(console, "Connected Services")

    manager = IntegrationManager()
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold #7c6af7")
    table.add_column("Service", style="#cccccc", min_width=16)
    table.add_column("Status", min_width=14)
    table.add_column("Required env", style="dim")

    for service in manager.list_services():
        if service["configured"]:
            status = "[#4caf50]configured[/]"
            missing = "-"
        else:
            status = "[#e0a020]missing config[/]"
            missing = ", ".join(service["missing_env"])
        table.add_row(service["name"], status, missing)

    console.print(table)
    pause(console)


def configure_integration(console: Console, service_key: str) -> bool:
    from voidcli.services.integrations import IntegrationManager

    manager = IntegrationManager()
    service = next(item for item in manager.list_services() if item["key"] == service_key)
    missing = service["missing_env"]

    if not missing:
        should_update = questionary.confirm(
            f"  {service['name']} is already configured. Update saved values?",
            default=False,
            style=STYLE,
        ).ask()
        if not should_update:
            return True
        required_env = tuple(service["required_env"])
    else:
        required_env = tuple(missing)

    section_header(console, f"Configure {service['name']}")
    console.print(Panel(
        f"VOIDCLI will save these values to [bold]{_env_path()}[/].\n"
        "Leave a value blank to skip setup and return to the integrations menu.",
        border_style="#3a3a3a",
        title="[#7c6af7]setup[/]",
        title_align="left",
    ))

    values = {}
    for env_name in required_env:
        current_value = os.getenv(env_name, "")
        prompt = f"  {env_name}:"

        if _is_sensitive_env(env_name):
            value = questionary.password(prompt, style=STYLE).ask()
        else:
            value = questionary.text(prompt, default=current_value, style=STYLE).ask()

        if not value:
            warn(console, "Configuration skipped.")
            pause(console)
            return False

        if "\n" in value or "\r" in value:
            error(console, f"{env_name} cannot contain new lines.")
            pause(console)
            return False

        values[env_name] = value.strip()

    _write_env_values(values)
    success(console, f"{service['name']} configuration saved.")

    test_now = questionary.confirm(
        "  Test connection now?",
        default=True,
        style=STYLE,
    ).ask()

    if test_now:
        spinning(console, f"Testing {service['name']}...")
        try:
            result = manager.execute(service_key, "status")
            console.print(Panel(
                json.dumps(result, indent=2, default=str),
                border_style="#7c6af7",
                title=f"[bold #7c6af7]{service['name']} status[/]",
                title_align="left",
                padding=(1, 2),
            ))
        except Exception as exc:
            warn(console, f"Saved, but status check failed: {exc}")
        pause(console)

    return True


def run_integration_action(console: Console, service_key: str):
    from voidcli.services.integrations import IntegrationManager

    manager = IntegrationManager()
    service = next(item for item in manager.list_services() if item["key"] == service_key)

    if not service["configured"]:
        configured = configure_integration(console, service_key)
        if not configured:
            return
        manager = IntegrationManager()
        service = next(item for item in manager.list_services() if item["key"] == service_key)

    section_header(console, service["name"])

    choices = [
        questionary.Choice("Configure / Update Credentials", value="configure"),
    ]
    choices.extend(
        questionary.Choice(action.replace("_", " ").title(), value=action)
        for action in service["actions"]
    )
    choices.extend([
        questionary.Separator(),
        questionary.Choice("Back", value="back"),
    ])

    action = questionary.select(
        "  Choose an action:",
        choices=choices,
        style=STYLE,
    ).ask()

    if action == "back" or action is None:
        return
    if action == "configure":
        configure_integration(console, service_key)
        return

    args = {}
    if action != "status":
        raw_args = questionary.text(
            "  Args as JSON (blank for none):",
            default="{}",
            style=STYLE,
        ).ask()
        if raw_args:
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError as exc:
                error(console, f"Invalid JSON: {exc}")
                pause(console)
                return

    spinning(console, f"Running {service['name']} {action}...")
    try:
        result = manager.execute(service_key, action, **args)
        console.print(Panel(
            json.dumps(result, indent=2, default=str),
            border_style="#7c6af7",
            title=f"[bold #7c6af7]{service['name']} - {action}[/]",
            title_align="left",
            padding=(1, 2),
        ))
    except Exception as exc:
        error(console, str(exc))

    pause(console)


def integrations_menu(console: Console):
    from voidcli.services.integrations import IntegrationManager

    manager = IntegrationManager()

    while True:
        section_header(console, "Integrations")

        choice = questionary.select(
            "  Choose a service:",
            choices=[
                questionary.Choice(
                    f"{service['name']} ({'configured' if service['configured'] else 'missing config'})",
                    value=service["key"],
                )
                for service in manager.list_services()
            ] + [
                questionary.Separator(),
                questionary.Choice("Connected Services", value="connected"),
                questionary.Choice("Back", value="back"),
            ],
            style=STYLE,
            instruction=" (arrows to navigate)",
        ).ask()

        if choice == "back" or choice is None:
            return
        if choice == "connected":
            show_connected_services(console)
        else:
            run_integration_action(console, choice)


def agentic_works(console: Console, gateway=None, orchestrator=None):
    section_header(console, "Agentic Works")

    console.print(Panel(
        "[bold]Agentic Works turns common repo tasks into an assistant job.[/]\n\n"
        "Preview mode: reads the repo and prints a plan or answer.\n"
        "Apply mode: lets the assistant use tools to create or edit files.\n\n"
        "Use Preview when you are exploring. Use Apply only when you want files changed.",
        border_style="#3a3a3a",
        title="[#7c6af7]how it works[/]",
        title_align="left",
    ))

    task = questionary.select(
        "  Choose a task:",
        choices=[
            questionary.Choice("Generate README", value="readme"),
            questionary.Choice("Explain Project", value="explain"),
            questionary.Choice("Find Bugs", value="bugs"),
            questionary.Choice("Create Tests", value="tests"),
            questionary.Choice("Code Refactor", value="refactor"),
            questionary.Separator(),
            questionary.Choice("Back", value="back"),
        ],
        style=STYLE,
    ).ask()

    if task == "back" or task is None:
        return

    repo_root = ask_for_repository(console)
    if repo_root is None:
        pause(console)
        return

    mode = questionary.select(
        "  How should VOIDCLI run this task?",
        choices=[
            questionary.Choice("Preview only - explain/plan, do not edit files", value="preview"),
            questionary.Choice("Apply changes - allow file edits when needed", value="apply"),
            questionary.Choice("Back", value="back"),
        ],
        style=STYLE,
    ).ask()

    if mode == "back" or mode is None:
        return

    labels = {
        "readme": "Generate README",
        "explain": "Explain Project",
        "bugs": "Find Bugs",
        "tests": "Create Tests",
        "refactor": "Code Refactor",
    }
    mode_instruction = (
        "Preview only. Do not write, delete, or modify files. Read files as needed and return a clear plan/result."
        if mode == "preview"
        else "Apply changes. You may write or modify files if needed, but keep changes focused and explain what changed."
    )
    prompt = (
        f"{labels[task]} for this Git repository: {repo_root}\n\n"
        f"Mode: {mode_instruction}\n\n"
        "Use available tools only when necessary. Prefer reading the repo before deciding what to do."
    )
    spinning(console, f"Running: {labels[task]}...")

    if gateway is None or orchestrator is None:
        console.print(Panel(
            f"[dim]Agentic task [bold #c4b5fd]{labels[task]}[/] is not connected to the main app.[/]",
            border_style="#3a3a3a",
            title=f"[#7c6af7]{labels[task].lower()}[/]",
            title_align="left",
        ))
        pause(console)
        return

    gateway.receive(prompt)
    orchestrator.run()
    pause(console)


def ask_for_input(console: Console):
    while True:
        choice = questionary.select(
            "  What would you like to do?",
            choices=[
                questionary.Choice("Analyze Repository", value="analyze"),
                questionary.Choice("Review Code", value="review"),
                questionary.Choice("Search for a File", value="search"),
                questionary.Choice("Integrations", value="integrations"),
                questionary.Choice("Agentic Works", value="agentic"),
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
            agentic_works(console)
        elif choice == "exit" or choice is None:
            console.print()
            console.rule(style="#3a3a3a")
            console.print("[dim #7c6af7]  goodbye - codesense v1.0.0[/]\n")
            break
