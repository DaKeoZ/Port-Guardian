# Port-Guardian

Outil CLI pour gérer et surveiller les ports TCP/UDP en écoute sur Linux et macOS. Idéal pour identifier rapidement quel processus occupe un port et libérer celui-ci en cas de conflit.

## Description

Port-Guardian scanne les connexions réseau en état **LISTEN** via `psutil`, affiche un tableau détaillé (port, protocole, statut, nom du processus, utilisateur, chemin de l’exécutable) et permet de terminer proprement le processus associé à un port pour le libérer.

- **Tableau Rich** : affichage coloré (TCP en cyan, UDP en jaune) avec barre de progression de scan.
- **Filtres** : recherche par nom de processus, affichage TCP ou UDP uniquement.
- **Action kill** : arrêt propre (`SIGTERM`) puis forcé (`SIGKILL`) après 2 secondes si besoin, avec confirmation.

## Pourquoi ce projet ?

Sur un **VPS** ou un serveur, un service peut refuser de démarrer parce qu’un autre processus occupe déjà le port (ex. 80, 443, 8080). Sans outil dédié, il faut enchaîner `netstat`/`ss`/`lsof` et chercher le PID à la main. Port-Guardian centralise tout : un seul outil pour **voir** qui écoute sur quels ports et **libérer** un port en une commande, avec confirmation pour éviter les erreurs.

## Installation

```bash
git clone <url-du-repo>
cd Port-Guardian
pip install -r requirements.txt
```

**Dépendances :** Python 3.7+, `psutil`, `rich` (voir `requirements.txt`).

## Usage

### Tableau des ports en écoute (par défaut)

```bash
python guardian.py
```

Affiche le panneau d’accueil, lance un scan avec barre de progression, puis un tableau de tous les ports TCP/UDP en écoute.

### Filtrage

```bash
# Uniquement les processus dont le nom contient "nginx"
python guardian.py --search nginx

# Uniquement les ports TCP
python guardian.py --tcp-only

# Uniquement les ports UDP
python guardian.py --udp-only

# Combinaison : processus "java" en TCP
python guardian.py --search java --tcp-only
```

Le titre du tableau s’adapte aux filtres actifs (ex. « processus "nginx" », « TCP uniquement »).

### Libérer un port (kill)

```bash
python guardian.py --kill 8080
```

Le programme trouve le(s) PID en écoute sur le port **8080**, demande confirmation :

```
Êtes-vous sûr de vouloir libérer le port 8080 ? [y/N]
```

Sur **y** ou **yes**, il envoie d’abord `terminate()`, attend 2 secondes, puis `kill()` si le processus est encore actif. Un message confirme la libération du port.

## Structure du projet

```
Port-Guardian/
├── guardian.py      # Point d'entrée CLI (argparse, affichage Rich)
├── scanner.py       # Scan des ports (psutil), get_listening_ports(), get_pids_for_port()
├── actions.py       # kill_process(pid) — arrêt propre puis forcé
├── requirements.txt
└── README.md
```

## Licence

Projet personnel — utilisation libre.
