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
        console.print("  [yellow](Lista vacía)[/yellow]")
        return

    table = Table(title="Skills configuradas para este proyecto", show_lines=True)
    table.add_column("Repositorio", style="cyan")
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
    console.print(f"[green]✓ Añadida:[/green] {skill_name} ({url})")


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

    console.print(f"[yellow]- Eliminada:[/yellow] {skill_name} de la configuración.")


def setup_antigravity_symlink() -> None:
    source_dir = Path.home() / ".agents" / "skills"
    target_dir = Path.home() / ".gemini" / "antigravity" / "skills"

    if not source_dir.is_dir():
        return

    if not target_dir.exists() and not target_dir.is_symlink():
        console.print("\n[blue]Configurando symlink para Antigravity...[/blue]")
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(source_dir, target_dir)
        console.print(f"  [green]✓ Symlink creado:[/green] {target_dir} -> {source_dir}")


def process_skills(force_update: bool = False) -> None:
    header()

    if force_update:
        console.print("[blue]Iniciando ACTUALIZACIÓN FORZADA de todas las skills...[/blue]")
        with open(INSTALLED_FILE, "w") as f:
            f.write("")
    else:
        console.print("[blue]Iniciando sincronización...[/blue]")

    data = load_skills()
    repos = data.get("repositories", [])

    if not repos:
        console.print("[yellow]No hay skills en la lista para procesar.[/yellow]")
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
            if not force_update and skill in installed:
                console.print(f"⚡ [yellow]Saltando:[/yellow] {skill}")
                continue

            console.print(f"\n📦 Repo: [cyan]{url}[/cyan]")
            console.print(f"🚀 Instalando: [green]{skill}[/green]")

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
                    console.print("  [green]✓ Instalación exitosa[/green]")
                    installed.add(str(skill))
                else:
                    console.print("  [red]✗ Falló la instalación[/red]")
            except FileNotFoundError:
                console.print("  [red]✗ Error: 'npx' no encontrado[/red]")

    with open(INSTALLED_FILE, "w") as f:
        f.write("\n".join(sorted(installed)) + "\n")

    setup_antigravity_symlink()
    console.print("\n[green]Proceso finalizado.[/green]")


def cleanup_local() -> None:
    console.print("[blue]Limpiando contaminación local del workspace...[/blue]")
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

    console.print("[green]✓ Workspace impecable.[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="SRE Skills Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("sync", help="Instala solo las skills nuevas o faltantes")
    subparsers.add_parser(
        "update", help="Fuerza la actualización/reinstalación de TODAS las skills"
    )
    subparsers.add_parser("list", help="Lista las skills configuradas en el proyecto")
    subparsers.add_parser("clean", help="Limpia carpetas ocultas locales")

    add_parser = subparsers.add_parser("add", help="Añade una nueva skill a la lista")
    add_parser.add_argument("url", help="URL del repositorio")
    add_parser.add_argument("name", help="Nombre de la skill")

    remove_parser = subparsers.add_parser("remove", help="Quita una skill de la lista")
    remove_parser.add_argument("name", help="Nombre de la skill")

    args = parser.parse_args()

    if args.command == "sync":
        process_skills(force_update=False)
    elif args.command == "update":
        process_skills(force_update=True)
    elif args.command == "list":
        list_skills()
    elif args.command == "add":
        add_skill(args.url, args.name)
    elif args.command == "remove":
        remove_skill(args.name)
    elif args.command == "clean":
        cleanup_local()


if __name__ == "__main__":
    main()
