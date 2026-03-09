#!/usr/bin/env python3
"""
Port-Guardian — Point d'entrée CLI pour lister les ports en écoute.
"""

import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from scanner import get_listening_ports

console = Console()

# Couleurs par protocole
COLOR_TCP = "cyan"
COLOR_UDP = "yellow"
COLOR_STATUS = "green"


def display_dashboard(ports):
    """
    Affiche un tableau stylisé des ports en écoute avec couleurs TCP/UDP et status.
    """
    table = Table(
        title="Port-Guardian Dashboard",
        show_header=True,
        header_style="bold white",
        border_style="dim",
    )
    table.add_column("Port", style="bold", justify="right", width=8)
    table.add_column("Protocole", width=10)
    table.add_column("Status", width=10)
    table.add_column("Processus", width=18)
    table.add_column("Utilisateur", width=14)
    table.add_column("Exécutable", width=40, overflow="ellipsis")

    for port, protocol, status, process_name, username, exe_path in ports:
        protocol_style = COLOR_TCP if protocol == "TCP" else COLOR_UDP
        table.add_row(
            str(port),
            f"[{protocol_style}]{protocol}[/]",
            f"[{COLOR_STATUS}]{status}[/]",
            process_name,
            username,
            exe_path or "—",
        )

    console.print(table)


def run_scan_with_progress():
    """
    Lance le scan des ports avec une barre de progression.
    Retourne la liste des connexions en écoute.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scan système...", total=None)
        progress.update(task, description="Analyse des interfaces réseau...")
        time.sleep(0.4)
        progress.update(task, description="Collecte des connexions TCP/UDP...")
        ports = get_listening_ports()
        progress.update(task, description="Résolution des processus (PID → nom)...")
        time.sleep(0.3)
        progress.update(task, description="[green]Scan terminé.[/]")
        time.sleep(0.2)
    return ports


def main():
    # Panneau d'accueil
    console.print(
        Panel(
            "[bold]Port-Guardian[/] — Surveillance des ports TCP/UDP en écoute\n"
            "Scan des connexions système et résolution des processus.",
            title="[bold cyan]Bienvenue[/]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    # Scan avec barre de progression
    ports = run_scan_with_progress()
    console.print()

    # Tableau des résultats
    if ports:
        display_dashboard(ports)
    else:
        console.print("[yellow]Aucun port en écoute trouvé (ou accès refusé).[/]")


if __name__ == "__main__":
    main()
