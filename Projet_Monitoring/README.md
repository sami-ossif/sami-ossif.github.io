# SysWatch — moniteur réseau & système en ligne de commande

Outil d'administration écrit **en Python pur** (bibliothèque standard uniquement,
**aucune dépendance à installer**). Il regroupe quatre fonctions utiles au
quotidien d'un technicien systèmes & réseaux :

| Commande | Rôle |
|----------|------|
| `scan`   | Scanner les ports TCP ouverts d'une machine |
| `check`  | Vérifier la disponibilité d'une liste de services (fichier JSON) |
| `disk`   | Afficher l'utilisation des disques |
| `watch`  | Surveiller des services en continu et journaliser les changements d'état |

## Pourquoi ce projet

Je voulais un petit outil de supervision que je comprends de bout en bout, sans
boîte noire. Tout repose sur la bibliothèque standard (`socket`, `shutil`,
`concurrent.futures`, `argparse`, `json`), ce qui le rend **portable** (Windows,
Linux, macOS) et **exécutable partout** sans `pip install`.

Ce projet m'a permis de travailler :
- la programmation réseau bas niveau avec les *sockets* TCP ;
- la **concurrence** (scan de ports parallélisé avec un pool de threads) ;
- la conception d'une **CLI** propre avec sous-commandes (`argparse`) ;
- l'écriture de **tests unitaires** (`unittest`), y compris contre un vrai
  serveur TCP local éphémère ;
- de bonnes pratiques : codes de sortie exploitables en **CI / cron**, sortie
  JSON, code documenté.

## Prérequis

Python 3.10 ou supérieur. Rien d'autre.

## Utilisation

```bash
# Scanner les ports 1 à 1024 d'une machine
python syswatch.py scan 127.0.0.1 --ports 1-1024

# Scanner des ports précis
python syswatch.py scan exemple.com --ports 22,80,443

# Vérifier une liste de services (voir services.example.json)
python syswatch.py check services.example.json

# Sortie JSON (pour un dashboard ou un autre script)
python syswatch.py check services.example.json --json

# Utilisation disque
python syswatch.py disk            # disque racine
python syswatch.py disk C:\ D:\    # plusieurs volumes

# Surveillance continue avec journal des changements d'état
python syswatch.py watch services.example.json --interval 10 --log etat.log
```

### Exemple de sortie

```
ETAT   SERVICE              ADRESSE                  LATENCE
--------------------------------------------------------------
UP     Google DNS           8.8.8.8:53               24.4 ms
UP     GitHub               github.com:443           41.3 ms
DOWN   Serveur local        127.0.0.1:80             -
```

La commande `check` renvoie un **code de sortie `1`** si au moins un service est
indisponible, ce qui permet de l'intégrer facilement dans un pipeline
d'intégration continue ou une tâche planifiée.

## Format du fichier de services

```json
[
  { "nom": "GitHub", "hote": "github.com", "port": 443 },
  { "nom": "Base de données", "hote": "10.0.0.5", "port": 5432 }
]
```

## Tests

```bash
python -m unittest -v
```

## Note d'usage

Le scan de ports ne doit être utilisé que sur des machines qui vous
appartiennent ou pour lesquelles vous avez une autorisation explicite.

## Licence

MIT — voir le fichier `LICENSE`.
