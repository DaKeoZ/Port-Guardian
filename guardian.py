#!/usr/bin/env python3
"""
Port-Guardian — Point d'entrée CLI pour lister les ports en écoute.
"""

from scanner import get_listening_ports


def main():
    ports = get_listening_ports()
    for port, protocol, status, process_name, username, exe_path in ports:
        print(f"[{port}] [{protocol}] [{status}] [{process_name}] [{username}] [{exe_path}]")


if __name__ == "__main__":
    main()
