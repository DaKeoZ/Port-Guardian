#!/usr/bin/env python3
"""
Port-Guardian — Point d'entrée CLI pour lister les ports en écoute.
"""

import argparse
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

import psutil

from actions import kill_process
from scanner import get_listening_ports, get_pids_for_port

console = Console()

# Couleurs par protocole
COLOR_TCP = "cyan"
COLOR_UDP = "yellow"
COLOR_STATUS = "green"


def apply_filters(ports, args):
    """
    Filtre la liste des ports selon --search, --tcp-only, --udp-only.
    """
    result = list(ports)
    if args.search:
        term = args.search.lower()
        result = [
            row for row in result
            if term in (row[3] or "").lower()  # process_name
        ]
    if args.tcp_only:
        result = [row for row in result if row[1] == "TCP"]
    if args.udp_only:
        result = [row for row in result if row[1] == "UDP"]
    return result


def display_dashboard(ports, title="Port-Guardian Dashboard"):
    """
    Affiche un tableau stylisé des ports en écoute avec couleurs TCP/UDP et status.
    """
    table = Table(
        title=title,
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


def run_kill_port(port):
    """
    Trouve les PIDs associés au port, demande confirmation, puis exécute kill_process.
    """
    pids = get_pids_for_port(port)
    if not pids:
        console.print(f"[red]Aucun processus en écoute sur le port {port}.[/]")
        sys.exit(1)

    rep = input(f"Êtes-vous sûr de vouloir libérer le port {port} ? [y/N] ").strip().lower()
    if rep not in ("y", "yes"):
        console.print("Annulé.")
        return

    for pid in pids:
        try:
            kill_process(pid)
            console.print(f"[green]Processus {pid} arrêté. Port {port} libéré.[/]")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            console.print(f"[red]Impossible d'arrêter le processus {pid}: {e}[/]")
            sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Port-Guardian — Surveillance des ports en écoute.")
    parser.add_argument(
        "--kill",
        type=int,
        metavar="PORT",
        help="Libérer le port en arrêtant le processus associé (demande confirmation).",
    )
    filtres = parser.add_argument_group("filtres d'affichage")
    filtres.add_argument(
        "--search",
        type=str,
        metavar="NAME",
        help="N'afficher que les ports des processus dont le nom contient NAME (ex: nginx, java).",
    )
    proto = filtres.add_mutually_exclusive_group()
    proto.add_argument(
        "--tcp-only",
        action="store_true",
        help="N'afficher que les ports TCP.",
    )
    proto.add_argument(
        "--udp-only",
        action="store_true",
        help="N'afficher que les ports UDP.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.kill is not None:
        run_kill_port(args.kill)
        return

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

    # Application des filtres
    filtered = apply_filters(ports, args)
    title = "Port-Guardian Dashboard"
    parts = []
    if args.search:
        parts.append(f"processus « {args.search} »")
    if args.tcp_only:
        parts.append("TCP uniquement")
    if args.udp_only:
        parts.append("UDP uniquement")
    if parts:
        title += " — " + ", ".join(parts)

    if filtered:
        display_dashboard(filtered, title=title)
    elif ports:
        console.print("[yellow]Aucun port ne correspond aux filtres appliqués.[/]")
    else:
        console.print("[yellow]Aucun port en écoute trouvé (ou accès refusé).[/]")


if __name__ == "__main__":
    main()
