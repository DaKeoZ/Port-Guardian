#!/usr/bin/env python3
"""
Port-Guardian — Point d'entrée CLI pour lister les ports en écoute.
"""

from scanner import get_listening_ports


def main():
    ports = get_listening_ports()
    for port, protocol, status in ports:
        print(f"[{port}] [{protocol}] [{status}]")


if __name__ == "__main__":
    main()
