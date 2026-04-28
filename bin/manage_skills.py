#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pyyaml>=6.0.1",
#     "rich>=13.7.1"
# ]
# ///

import os
import subprocess
import yaml
import shutil
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

PROJECT_DIR = Path(__file__).resolve().parent.parent
SKILLS_FILE = PROJECT_DIR / "conf" / "skills.yaml"
GLOBAL_AGENTS_DIR = Path.home() / ".agents"
INSTALLED_FILE = GLOBAL_AGENTS_DIR / "skills.installed"


def ensure_dirs() -> None:
    (PROJECT_DIR / "conf").mkdir(parents=True, exist_ok=True)
    GLOBAL_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    if not SKILLS_FILE.exists():
        with open(SKILLS_FILE, "w") as f:
            yaml.dump({"repositories": []}, f)
    if not INSTALLED_FILE.exists():
        INSTALLED_FILE.touch()


def load_skills() -> dict[str, list[dict[str, str | list[str]]]]:
    ensure_dirs()
    with open(SKILLS_FILE, "r") as f:
        data = yaml.safe_load(f)
        if not data or "repositories" not in data:
            return {"repositories": []}
        return data  # type: ignore


def save_skills(data: dict[str, list[dict[str, str | list[str]]]]) -> None:
    with open(SKILLS_FILE, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def header() -> None:
    console.print("[cyan]  ██████╗██╗  ██╗██╗██╗     ██╗     ███████╗[/cyan]")
    console.print("[cyan]  ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝[/cyan]")
    console.print("[cyan]  ███████╗█████╔╝ ██║██║     ██║     ███████╗[/cyan]")
    console.print("[cyan]  ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║[/cyan]")
    console.print("[cyan]  ███████║██║  ██╗██║███████╗███████╗███████║[/cyan]")
    console.print("[cyan]  ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝[/cyan]")
    console.print("             [bold cyan]SRE Skills Manager v3.0[/bold cyan]\n")


def list_skills() -> None:
    header()
    data = load_skills()
    repos = data.get("repositories", [])

    if not repos:
        console.print("  [yellow](Empty list)[/yellow]")
        return

    table = Table(title="Skills configured for this project", show_lines=True)
    table.add_column("Repository", style="cyan")
    table.add_column("Skills", style="green")

    for repo in repos:
        url = str(repo.get("url", ""))
        skills = repo.get("skills", [])
        if isinstance(skills, list):
            table.add_row(url, "\n".join(str(s) for s in skills))

    console.print(table)


def add_skill(url: str, skill_name: str) -> None:
    data = load_skills()
    repos = data.get("repositories", [])

    found = False
    for repo in repos:
        if repo.get("url") == url:
            skills = repo.setdefault("skills", [])
            if isinstance(skills, list) and skill_name not in skills:
                skills.append(skill_name)
                skills.sort()
            found = True
            break

    if not found:
        repos.append({"url": url, "skills": [skill_name]})

    data["repositories"] = repos
    save_skills(data)
    console.print(f"[green]✓ Added:[/green] {skill_name} ({url})")


def remove_skill(skill_name: str) -> None:
    data = load_skills()
    repos = data.get("repositories", [])

    for repo in repos:
        skills = repo.get("skills", [])
        if isinstance(skills, list) and skill_name in skills:
            skills.remove(skill_name)

    # Clean up empty repos
    data["repositories"] = [r for r in repos if r.get("skills")]
    save_skills(data)

    # Remove from installed file
    if INSTALLED_FILE.exists():
        with open(INSTALLED_FILE, "r") as f:
            installed = set(f.read().splitlines())
        if skill_name in installed:
            installed.remove(skill_name)
            with open(INSTALLED_FILE, "w") as f:
                f.write("\n".join(sorted(installed)) + "\n")

    console.print(f"[yellow]- Removed:[/yellow] {skill_name} from configuration.")


def setup_antigravity_symlink() -> None:
    source_dir = Path.home() / ".agents" / "skills"
    target_dir = Path.home() / ".gemini" / "antigravity" / "skills"

    if not source_dir.is_dir():
        return

    if not target_dir.exists() and not target_dir.is_symlink():
        console.print("\n[blue]Configuring symlink for Antigravity...[/blue]")
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(source_dir, target_dir)
        console.print(f"  [green]✓ Symlink created:[/green] {target_dir} -> {source_dir}")


def inject_ide_rules() -> None:
    source_dir = Path.home() / ".agents" / "skills"
    if not source_dir.is_dir():
        console.print("[red]✗ Global skills directory not found. Please run sync first.[/red]")
        return
        
    cwd = Path.cwd()
    console.print(f"\n[blue]Injecting IDE skills into current project: {cwd}[/blue]")
    
    # 1. Cursor
    cursor_rules = cwd / ".cursor" / "rules"
    if not cursor_rules.exists() and not cursor_rules.is_symlink():
        cursor_rules.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(source_dir, cursor_rules)
        console.print(f"  [green]✓ Cursor:[/green] Created symlink {cursor_rules} -> {source_dir}")
    else:
        console.print("  [yellow]- Cursor:[/yellow] rules directory already exists, skipping.")

    # 2. Roo Code / Cline
    cline_rules_dir = cwd / ".roomodes"
    if not cline_rules_dir.exists() and not cline_rules_dir.is_symlink():
        os.symlink(source_dir, cline_rules_dir)
        console.print(f"  [green]✓ Roo Code:[/green] Created symlink {cline_rules_dir} -> {source_dir}")
    else:
        console.print("  [yellow]- Roo Code:[/yellow] .roomodes already exists, skipping.")

    console.print("\n[green]✓ IDE Injection complete.[/green] Add these paths to your .gitignore if needed.")



def process_skills(force_update: bool = False, target_skill: str | None = None) -> None:
    header()

    if force_update and not target_skill:
        console.print("[blue]Starting FORCED UPDATE of all skills...[/blue]")
        with open(INSTALLED_FILE, "w") as f:
            f.write("")
    elif force_update and target_skill:
        console.print(f"[blue]Starting UPDATE for skill: {target_skill}...[/blue]")
    else:
        console.print("[blue]Starting synchronization...[/blue]")

    data = load_skills()
    repos = data.get("repositories", [])

    if not repos:
        console.print("[yellow]No skills in the list to process.[/yellow]")
        return

    installed = set()
    if INSTALLED_FILE.exists():
        with open(INSTALLED_FILE, "r") as f:
            installed = set(f.read().splitlines())

    for repo in repos:
        url = repo.get("url")
        skills = repo.get("skills", [])

        if not url or not isinstance(skills, list):
            continue

        for skill in skills:
            if target_skill and skill != target_skill:
                continue

            # If force_update is True and target_skill matches, we skip 'installed' check
            if not force_update and skill in installed:
                console.print(f"⚡ [yellow]Skipping:[/yellow] {skill}")
                continue
            
            if force_update and target_skill == skill and skill in installed:
                installed.remove(skill)

            console.print(f"\n📦 Repo: [cyan]{url}[/cyan]")
            console.print(f"🚀 Installing: [green]{skill}[/green]")

            try:
                result = subprocess.run(
                    [
                        "npx",
                        "-y",
                        "skills",
                        "add",
                        str(url),
                        "--skill",
                        str(skill),
                        "--global",
                        "--yes",
                    ],
                    check=False,
                )
                if result.returncode == 0:
                    console.print("  [green]✓ Installation successful[/green]")
                    installed.add(str(skill))
                else:
                    console.print("  [red]✗ Installation failed[/red]")
            except FileNotFoundError:
                console.print("  [red]✗ Error: 'npx' not found[/red]")

    with open(INSTALLED_FILE, "w") as f:
        f.write("\n".join(sorted(installed)) + "\n")

    setup_antigravity_symlink()
    console.print("\n[green]Process finished.[/green]")


def cleanup_local() -> None:
    console.print("[blue]Cleaning up local workspace contamination...[/blue]")
    for item in PROJECT_DIR.iterdir():
        if (
            item.is_dir()
            and item.name.startswith(".")
            and item.name not in (".", "..", ".git")
            and not item.name.startswith(".skills")
        ):
            shutil.rmtree(item)

    for rm_item in ("skills", "skills-lock.json"):
        p = PROJECT_DIR / rm_item
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

    console.print("[green]✓ Pristine workspace.[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="SRE Skills Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("sync", help="Installs only new or missing skills")
    update_parser = subparsers.add_parser(
        "update", help="Forces update of a specific skill or ALL skills"
    )
    update_parser.add_argument(
        "name", nargs="?", help="Name of the skill to update (optional)"
    )
    subparsers.add_parser("list", help="Lists the configured skills in the project")
    subparsers.add_parser("clean", help="Cleans local hidden folders")
    subparsers.add_parser("inject", help="Injects global skills into local project IDE configs (Cursor, VSCode)")

    add_parser = subparsers.add_parser("add", help="Adds a new skill to the list")
    add_parser.add_argument("url", help="Repository URL")
    add_parser.add_argument("name", help="Skill name")

    remove_parser = subparsers.add_parser("remove", help="Removes a skill from the list")
    remove_parser.add_argument("name", help="Skill name")

    args = parser.parse_args()

    if args.command == "sync":
        process_skills(force_update=False)
    elif args.command == "update":
        process_skills(force_update=True, target_skill=args.name)
    elif args.command == "list":
        list_skills()
    elif args.command == "add":
        add_skill(args.url, args.name)
    elif args.command == "remove":
        remove_skill(args.name)
    elif args.command == "clean":
        cleanup_local()
    elif args.command == "inject":
        inject_ide_rules()


if __name__ == "__main__":
    main()
