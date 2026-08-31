#!/usr/bin/env python3
"""SysWatch — moniteur reseau & systeme en ligne de commande.

Outil d'administration systeme ecrit uniquement avec la bibliotheque standard
de Python (aucune dependance a installer). Il permet de :

  * scanner les ports TCP ouverts d'une machine (commande `scan`) ;
  * verifier la disponibilite d'une liste de services host:port (commande `check`) ;
  * afficher l'espace disque des points de montage (commande `disk`) ;
  * surveiller des services en continu et journaliser les changements (commande `watch`).

Auteur : Sami OSSIF
Licence : MIT
"""

from __future__ import annotations

import argparse
import json
import socket
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------- #
# Petites briques utilitaires
# --------------------------------------------------------------------------- #

# Quelques ports courants, utilises pour donner un nom lisible dans la sortie.
PORTS_CONNUS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 143: "imap", 443: "https", 445: "smb",
    3306: "mysql", 3389: "rdp", 5432: "postgres", 6379: "redis", 8080: "http-alt",
}


def horodatage() -> str:
    """Renvoie l'horodatage UTC courant au format ISO 8601 (a la seconde)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def tester_port(hote: str, port: int, timeout: float = 1.0) -> tuple[bool, float | None]:
    """Tente une connexion TCP sur hote:port.

    Renvoie un couple (ouvert, latence_ms). La latence n'est mesuree que si la
    connexion aboutit ; sinon elle vaut None.
    """
    debut = time.perf_counter()
    try:
        with socket.create_connection((hote, port), timeout=timeout):
            latence_ms = (time.perf_counter() - debut) * 1000
            return True, round(latence_ms, 1)
    except (OSError, socket.gaierror):
        return False, None


def parser_plage_ports(expression: str) -> list[int]:
    """Transforme une expression de ports en liste d'entiers.

    Accepte les formats "80", "1-1024" et "22,80,443". Les valeurs hors de
    l'intervalle 1-65535 declenchent une erreur explicite.
    """
    ports: set[int] = set()
    for morceau in expression.split(","):
        morceau = morceau.strip()
        if not morceau:
            continue
        if "-" in morceau:
            debut_txt, fin_txt = morceau.split("-", 1)
            debut, fin = int(debut_txt), int(fin_txt)
            if debut > fin:
                debut, fin = fin, debut
            ports.update(range(debut, fin + 1))
        else:
            ports.add(int(morceau))
    invalides = [p for p in ports if not 1 <= p <= 65535]
    if invalides:
        raise ValueError(f"Ports hors intervalle 1-65535 : {sorted(invalides)}")
    return sorted(ports)


def formater_octets(nb_octets: int) -> str:
    """Convertit un nombre d'octets en chaine lisible (Ko, Mo, Go, To)."""
    taille = float(nb_octets)
    for unite in ("o", "Ko", "Mo", "Go", "To"):
        if taille < 1024 or unite == "To":
            return f"{taille:.1f} {unite}"
        taille /= 1024
    return f"{taille:.1f} To"


# --------------------------------------------------------------------------- #
# Modele de resultat
# --------------------------------------------------------------------------- #

@dataclass
class ResultatService:
    """Resultat de la verification d'un service (host:port)."""
    nom: str
    hote: str
    port: int
    disponible: bool
    latence_ms: float | None
    horodatage: str


# --------------------------------------------------------------------------- #
# Commande : scan
# --------------------------------------------------------------------------- #

def commande_scan(hote: str, ports: list[int], timeout: float, threads: int) -> int:
    """Scanne les ports TCP de `hote` et affiche ceux qui sont ouverts."""
    print(f"[scan] cible {hote} — {len(ports)} port(s), {threads} threads\n")
    ouverts: list[tuple[int, float]] = []

    with ThreadPoolExecutor(max_workers=threads) as pool:
        futurs = {pool.submit(tester_port, hote, p, timeout): p for p in ports}
        for futur in as_completed(futurs):
            port = futurs[futur]
            ouvert, latence = futur.result()
            if ouvert:
                ouverts.append((port, latence or 0.0))

    if not ouverts:
        print("Aucun port ouvert detecte.")
        return 0

    print(f"{'PORT':>6}  {'SERVICE':<10}  LATENCE")
    print("-" * 30)
    for port, latence in sorted(ouverts):
        service = PORTS_CONNUS.get(port, "?")
        print(f"{port:>6}  {service:<10}  {latence:>5.1f} ms")
    print(f"\n{len(ouverts)} port(s) ouvert(s).")
    return 0


# --------------------------------------------------------------------------- #
# Commande : check
# --------------------------------------------------------------------------- #

def charger_services(chemin: Path) -> list[dict]:
    """Charge une liste de services depuis un fichier JSON.

    Format attendu : [{"nom": "...", "hote": "...", "port": 443}, ...]
    """
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    if not isinstance(donnees, list):
        raise ValueError("Le fichier de services doit contenir une liste JSON.")
    return donnees


def verifier_services(services: list[dict], timeout: float, threads: int) -> list[ResultatService]:
    """Verifie la disponibilite de chaque service en parallele."""
    resultats: list[ResultatService] = []

    def _verifier(svc: dict) -> ResultatService:
        hote, port = svc["hote"], int(svc["port"])
        disponible, latence = tester_port(hote, port, timeout)
        return ResultatService(
            nom=svc.get("nom", f"{hote}:{port}"),
            hote=hote,
            port=port,
            disponible=disponible,
            latence_ms=latence,
            horodatage=horodatage(),
        )

    with ThreadPoolExecutor(max_workers=threads) as pool:
        for resultat in pool.map(_verifier, services):
            resultats.append(resultat)
    return resultats


def commande_check(chemin: Path, timeout: float, threads: int, json_sortie: bool) -> int:
    """Verifie une liste de services et affiche un tableau UP/DOWN."""
    services = charger_services(chemin)
    resultats = verifier_services(services, timeout, threads)

    if json_sortie:
        print(json.dumps([asdict(r) for r in resultats], ensure_ascii=False, indent=2))
    else:
        print(f"{'ETAT':<6} {'SERVICE':<20} {'ADRESSE':<24} LATENCE")
        print("-" * 62)
        for r in resultats:
            etat = "UP" if r.disponible else "DOWN"
            latence = f"{r.latence_ms:.1f} ms" if r.latence_ms is not None else "-"
            print(f"{etat:<6} {r.nom:<20} {r.hote + ':' + str(r.port):<24} {latence}")

    hors_service = [r for r in resultats if not r.disponible]
    if hors_service and not json_sortie:
        print(f"\n{len(hors_service)} service(s) indisponible(s).")
    # Code de sortie non nul si au moins un service est down (utile en CI / cron).
    return 1 if hors_service else 0


# --------------------------------------------------------------------------- #
# Commande : disk
# --------------------------------------------------------------------------- #

def commande_disk(chemins: list[str]) -> int:
    """Affiche l'utilisation disque des chemins fournis (racine par defaut)."""
    if not chemins:
        chemins = ["C:\\" if sys.platform.startswith("win") else "/"]

    print(f"{'MONTAGE':<16} {'TAILLE':>10} {'UTILISE':>10} {'LIBRE':>10}  OCCUPATION")
    print("-" * 66)
    for chemin in chemins:
        try:
            usage = shutil.disk_usage(chemin)
        except OSError as err:
            print(f"{chemin:<16} erreur : {err}")
            continue
        pourcentage = usage.used / usage.total * 100 if usage.total else 0
        barre = "#" * round(pourcentage / 10) + "." * (10 - round(pourcentage / 10))
        print(
            f"{chemin:<16} {formater_octets(usage.total):>10} "
            f"{formater_octets(usage.used):>10} {formater_octets(usage.free):>10}  "
            f"[{barre}] {pourcentage:4.1f}%"
        )
    return 0


# --------------------------------------------------------------------------- #
# Commande : watch
# --------------------------------------------------------------------------- #

def commande_watch(chemin: Path, intervalle: float, timeout: float,
                   threads: int, fichier_log: Path | None) -> int:
    """Surveille les services en continu et journalise les changements d'etat."""
    services = charger_services(chemin)
    etats_precedents: dict[str, bool] = {}
    print(f"[watch] {len(services)} service(s), intervalle {intervalle}s — Ctrl+C pour arreter\n")

    try:
        while True:
            resultats = verifier_services(services, timeout, threads)
            for r in resultats:
                ancien = etats_precedents.get(r.nom)
                if ancien is None or ancien != r.disponible:
                    etat = "UP" if r.disponible else "DOWN"
                    ligne = f"{r.horodatage}  {etat:<4}  {r.nom} ({r.hote}:{r.port})"
                    print(ligne)
                    if fichier_log is not None:
                        with fichier_log.open("a", encoding="utf-8") as f:
                            f.write(ligne + "\n")
                etats_precedents[r.nom] = r.disponible
            time.sleep(intervalle)
    except KeyboardInterrupt:
        print("\n[watch] arret demande par l'utilisateur.")
        return 0


# --------------------------------------------------------------------------- #
# Interface en ligne de commande
# --------------------------------------------------------------------------- #

def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="syswatch",
        description="Moniteur reseau & systeme en ligne de commande (Python, stdlib uniquement).",
    )
    sous = parseur.add_subparsers(dest="commande", required=True)

    p_scan = sous.add_parser("scan", help="scanner les ports TCP d'une machine")
    p_scan.add_argument("hote", help="adresse ou nom de la machine cible")
    p_scan.add_argument("--ports", default="1-1024", help="ports a scanner (ex : 1-1024, 22,80,443)")
    p_scan.add_argument("--timeout", type=float, default=1.0, help="timeout par port en secondes")
    p_scan.add_argument("--threads", type=int, default=100, help="nombre de connexions en parallele")

    p_check = sous.add_parser("check", help="verifier une liste de services (fichier JSON)")
    p_check.add_argument("fichier", type=Path, help="fichier JSON des services a verifier")
    p_check.add_argument("--timeout", type=float, default=2.0, help="timeout par service en secondes")
    p_check.add_argument("--threads", type=int, default=20, help="verifications en parallele")
    p_check.add_argument("--json", action="store_true", help="sortie au format JSON")

    p_disk = sous.add_parser("disk", help="afficher l'utilisation disque")
    p_disk.add_argument("chemins", nargs="*", help="points de montage a inspecter")

    p_watch = sous.add_parser("watch", help="surveiller des services en continu")
    p_watch.add_argument("fichier", type=Path, help="fichier JSON des services a surveiller")
    p_watch.add_argument("--interval", type=float, default=10.0, help="intervalle entre deux tours (s)")
    p_watch.add_argument("--timeout", type=float, default=2.0, help="timeout par service en secondes")
    p_watch.add_argument("--threads", type=int, default=20, help="verifications en parallele")
    p_watch.add_argument("--log", type=Path, default=None, help="fichier journal des changements d'etat")

    return parseur


def main(argv: list[str] | None = None) -> int:
    args = construire_parseur().parse_args(argv)

    if args.commande == "scan":
        try:
            ports = parser_plage_ports(args.ports)
        except ValueError as err:
            print(f"Erreur : {err}", file=sys.stderr)
            return 2
        return commande_scan(args.hote, ports, args.timeout, args.threads)

    if args.commande == "check":
        return commande_check(args.fichier, args.timeout, args.threads, args.json)

    if args.commande == "disk":
        return commande_disk(args.chemins)

    if args.commande == "watch":
        return commande_watch(args.fichier, args.interval, args.timeout, args.threads, args.log)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
