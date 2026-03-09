"""
Module de scan des ports en écoute (TCP/UDP) via psutil.
"""

import socket

import psutil


def get_listening_ports():
    """
    Liste tous les ports TCP et UDP actuellement en état LISTEN.

    Returns:
        list: Liste de tuples (port, protocole, status).
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

        result.append((port, protocol, conn.status))

    # Dédupliquer et trier
    seen = set()
    unique = []
    for port, protocol, status in sorted(result, key=lambda x: (x[0], x[1])):
        key = (port, protocol)
        if key not in seen:
            seen.add(key)
            unique.append((port, protocol, status))

    return unique
