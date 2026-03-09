"""
Module de scan des ports en écoute (TCP/UDP) via psutil.
"""

import socket

import psutil

# Valeur affichée lorsque l'accès au processus est refusé (ex. processus root)
_UNAVAILABLE = "—"


def _get_process_info(pid):
    """
    Récupère le nom, l'utilisateur et le chemin de l'exécutable pour un PID.
    Retourne (_UNAVAILABLE, ...) en cas d'AccessDenied ou PID invalide.
    """
    if pid is None:
        return _UNAVAILABLE, _UNAVAILABLE, _UNAVAILABLE
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        username = proc.username()
        try:
            exe = proc.exe()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            exe = _UNAVAILABLE
        return name, username, exe
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return _UNAVAILABLE, _UNAVAILABLE, _UNAVAILABLE


def get_listening_ports():
    """
    Liste tous les ports TCP et UDP actuellement en état LISTEN,
    avec nom du processus, utilisateur et chemin de l'exécutable.

    Returns:
        list: Liste de tuples (port, protocole, status, process_name, username, exe_path).
    """
    result = []
    try:
        connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, psutil.Error):
        return result

    for conn in connections:
        if conn.status != "LISTEN":
            continue
        if conn.laddr is None:
            continue

        port = conn.laddr.port
        if conn.type == socket.SOCK_STREAM:
            protocol = "TCP"
        elif conn.type == socket.SOCK_DGRAM:
            protocol = "UDP"
        else:
            protocol = "OTHER"

        name, username, exe = _get_process_info(conn.pid)
        result.append((port, protocol, conn.status, name, username, exe))

    # Dédupliquer et trier
    seen = set()
    unique = []
    for row in sorted(result, key=lambda x: (x[0], x[1])):
        port, protocol, status, name, username, exe = row
        key = (port, protocol)
        if key not in seen:
            seen.add(key)
            unique.append((port, protocol, status, name, username, exe))

    return unique


def get_pids_for_port(port):
    """
    Retourne l'ensemble des PIDs des processus en écoute sur le port donné (TCP ou UDP).

    Args:
        port: Numéro de port (int).

    Returns:
        set: Ensemble des PIDs, ou set vide si aucun ou accès refusé.
    """
    pids = set()
    try:
        connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, psutil.Error):
        return pids

    for conn in connections:
        if conn.status != "LISTEN" or conn.laddr is None:
            continue
        if conn.laddr.port == port and conn.pid is not None:
            pids.add(conn.pid)

    return pids
