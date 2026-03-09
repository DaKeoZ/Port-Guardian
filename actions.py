"""
Module d'actions sur les processus (arrêt propre ou forcé).
"""

import psutil


def kill_process(pid):
    """
    Arrête un processus : d'abord un arrêt propre (terminate()), puis
    arrêt forcé (kill()) après 2 secondes si le processus est encore actif.

    Args:
        pid: Identifiant du processus.

    Raises:
        psutil.NoSuchProcess: Si le processus n'existe pas.
        psutil.AccessDenied: Si les permissions sont insuffisantes.
    """
    proc = psutil.Process(pid)
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except psutil.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)
