#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rich>=13.7.1"
# ]
# ///

import os
import sys
import subprocess
import shutil
from pathlib import Path
from rich.console import Console
from rich.prompt import IntPrompt

console = Console()

PROJECT_DIR = Path(__file__).resolve().parent.parent
SKILLS_FILE = PROJECT_DIR / "conf" / "skills.yaml"
ENV_DIR = PROJECT_DIR / "environments"
GLOBAL_SKILLS_DIR = Path.home() / ".agents" / "skills"


def header() -> None:
    console.print("[cyan]  ╔════════════════════════════════════════╗[/cyan]")
    console.print("[cyan]  ║                                        ║[/cyan]")
    console.print("[cyan]  ║        AI Environment Bootstrapper     ║[/cyan]")
    console.print("[cyan]  ║                                        ║[/cyan]")
    console.print("[cyan]  ╚════════════════════════════════════════╝[/cyan]\n")


def install_core_skills() -> None:
    console.print("[blue]1. Installing base skills for the AI environment...[/blue]")

    if not SKILLS_FILE.is_file():
        console.print(f"[red]Error:[/red] Could not find file {SKILLS_FILE}")
        sys.exit(1)

    console.print("[yellow]Executing manage_skills.py sync...[/yellow]")
    manage_skills_script = PROJECT_DIR / "bin" / "manage_skills.py"
    subprocess.run([sys.executable, str(manage_skills_script), "sync"], check=True)


def setup_antigravity_env() -> None:
    console.print("\n[cyan][Antigravity][/cyan] Configuring environment...")
    target_gemini_dir = Path.home() / ".gemini"
    target_antigravity_skills = target_gemini_dir / "antigravity" / "skills"

    # Link Skills
    if GLOBAL_SKILLS_DIR.is_dir():
        target_antigravity_skills.parent.mkdir(parents=True, exist_ok=True)
        if not target_antigravity_skills.exists() and not target_antigravity_skills.is_symlink():
            os.symlink(GLOBAL_SKILLS_DIR, target_antigravity_skills)
            console.print(f"  [green]✓ Symlink created:[/green] {target_antigravity_skills}")

    # Install Rules (.gemini/GEMINI.md)
    gemini_rules_src = ENV_DIR / "antigravity" / "GEMINI.md"
    if gemini_rules_src.is_file():
        target_gemini_dir.mkdir(parents=True, exist_ok=True)
        target_gemini_dest = target_gemini_dir / "GEMINI.md"
        shutil.copy2(gemini_rules_src, target_gemini_dest)
        console.print(f"  [green]✓ Rules injected:[/green] {target_gemini_dest}")


def setup_cursor_env() -> None:
    console.print("\n[cyan][Cursor][/cyan] Configuring local environment...")
    cursor_rules_src = ENV_DIR / "cursor" / "cursorrules.template"
    if cursor_rules_src.is_file():
        target_cursor_rules = Path.cwd() / ".cursorrules"
        if not target_cursor_rules.is_file():
            shutil.copy2(cursor_rules_src, target_cursor_rules)
            console.print(
                f"  [green]✓ Created:[/green] .cursorrules in current project ({Path.cwd()})"
            )
        else:
            console.print("  [yellow]✓ .cursorrules already exists in project. Skipped.[/yellow]")


def setup_claude_env() -> None:
    console.print("\n[cyan][Claude][/cyan] Configuring local environment...")
    claude_rules_src = ENV_DIR / "claude" / "CLAUDE.md"
    if claude_rules_src.is_file():
        target_claude_rules = Path.cwd() / "CLAUDE.md"
        if not target_claude_rules.is_file():
            shutil.copy2(claude_rules_src, target_claude_rules)
            console.print(
                f"  [green]✓ Created:[/green] CLAUDE.md in current project ({Path.cwd()})"
            )
        else:
            console.print("  [yellow]✓ CLAUDE.md already exists in project. Skipped.[/yellow]")


def setup_roocode_env() -> None:
    console.print("\n[cyan][Roo Code / Cline][/cyan] Configuring local environment...")
    roo_rules_src = ENV_DIR / "roocode" / "roomodes.template"
    if roo_rules_src.is_file():
        target_roo_rules = Path.cwd() / ".clinerules"
        if not target_roo_rules.is_file():
            shutil.copy2(roo_rules_src, target_roo_rules)
            console.print(
                f"  [green]✓ Created:[/green] .clinerules in current project ({Path.cwd()})"
            )
        else:
            console.print("  [yellow]✓ .clinerules already exists in project. Skipped.[/yellow]")


def setup_copilot_env() -> None:
    console.print("\n[cyan][GitHub Copilot][/cyan] Configuring local environment...")
    copilot_rules_src = ENV_DIR / "copilot" / "copilot-instructions.template"
    if copilot_rules_src.is_file():
        target_dir = Path.cwd() / ".github"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_copilot_rules = target_dir / "copilot-instructions.md"
        if not target_copilot_rules.is_file():
            shutil.copy2(copilot_rules_src, target_copilot_rules)
            console.print(
                f"  [green]✓ Created:[/green] .github/copilot-instructions.md in current project ({Path.cwd()})"
            )
        else:
            console.print("  [yellow]✓ .github/copilot-instructions.md already exists. Skipped.[/yellow]")



def main() -> None:
    header()

    if not shutil.which("npx"):
        console.print(
            "[red]Error: NODE/NPX not detected. Please install it before continuing.[/red]"
        )
        sys.exit(1)

    install_core_skills()

    console.print("\n[blue]For which environment do you want to configure the system files?[/blue]")
    console.print("1) Antigravity (Gemini)")
    console.print("2) Cursor")
    console.print("3) Claude Code")
    console.print("4) Roo Code / Cline")
    console.print("5) GitHub Copilot")
    console.print("6) All")
    console.print("7) Exit")

    option = IntPrompt.ask("Choose an option", choices=[str(i) for i in range(1, 8)])

    if option == 1:
        setup_antigravity_env()
    elif option == 2:
        setup_cursor_env()
    elif option == 3:
        setup_claude_env()
    elif option == 4:
        setup_roocode_env()
    elif option == 5:
        setup_copilot_env()
    elif option == 6:
        setup_antigravity_env()
        setup_cursor_env()
        setup_claude_env()
        setup_roocode_env()
        setup_copilot_env()
    elif option == 7:
        console.print("Exiting...")
        sys.exit(0)

    console.print("\n[green]🚀 Environment configured successfully.[/green]")


if __name__ == "__main__":
    main()
