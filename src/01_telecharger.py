"""
01_telecharger.py — Téléchargement et inventaire du fichier source.

Ce script ne charge RIEN en base. Il récupère le fichier, calcule son
empreinte, et décrit ce qu'il contient réellement.

Objectif : trancher quatre questions avant d'écrire la moindre transformation.
  1. Quelles colonnes existent ?
  2. Quelle période est réellement couverte ?
  3. Le type de marché est-il présent ?        -> conditionne le test 2 (seuils)
  4. Y a-t-il un identifiant de fournisseur ?  -> conditionne le test 3

Usage :
    python src/01_telecharger.py
    python src/01_telecharger.py --forcer     (retélécharge même si déjà présent)
"""

import csv
import hashlib
import io
import sys
import urllib.request
from pathlib import Path

import pandas as pd
import yaml

RACINE = Path(__file__).resolve().parent.parent
CONFIG = RACINE / "config" / "params.yaml"
RAPPORT = RACINE / "sorties" / "inventaire.txt"

# Mots-clés utilisés pour repérer les colonnes candidates. Simple heuristique :
# le script propose, c'est l'humain qui tranche.
INDICES = {
    "montant":      ["montant", "valeur", "prix", "cout", "fcfa"],
    "date":         ["date", "annee", "exercice", "periode", "trimestre"],
    "fournisseur":  ["attributaire", "fournisseur", "titulaire", "entreprise",
                     "societe", "adjudicataire"],
    "autorite":     ["autorite", "contractante", "ministere", "organisme",
                     "maitre", "acheteur"],
    "type_marche":  ["type", "nature", "categorie", "objet"],
    "passation":    ["passation", "procedure", "mode", "methode"],
    "identifiant":  ["id", "code", "numero", "num", "reference", "ninea", "rccm"],
}


def charger_config():
    with io.open(CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)


def telecharger(url, destination, forcer=False):
    """Récupère le fichier. Ne retélécharge pas s'il est déjà là, sauf --forcer."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not forcer:
        print(f"  Déjà présent, pas de nouveau téléchargement : {destination.name}")
        print("  (relancer avec --forcer pour retélécharger)")
        return destination
    print(f"  Téléchargement depuis {url}")
    urllib.request.urlretrieve(url, destination)
    print(f"  Enregistré : {destination}")
    return destination


def empreinte(chemin):
    """SHA-256 du fichier : permet de détecter qu'une source a changé."""
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(65536), b""):
            h.update(bloc)
    return h.hexdigest()


def detecter_encodage(chemin):
    """Essaie les encodages du plus strict au plus permissif."""
    brut = chemin.read_bytes()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            brut.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin-1"  # ne échoue jamais, dernier recours


def detecter_separateur(chemin, encodage):
    with io.open(chemin, encoding=encodage, errors="replace") as f:
        echantillon = f.read(16384)
    try:
        return csv.Sniffer().sniff(echantillon, delimiters=";,\t|").delimiter
    except csv.Error:
        # Repli : on compte les occurrences sur la première ligne
        premiere = echantillon.splitlines()[0] if echantillon else ""
        return max(";,\t|", key=premiere.count)


def colonnes_candidates(colonnes):
    """Associe chaque rôle attendu aux colonnes dont le nom y ressemble."""
    resultat = {}
    for role, mots in INDICES.items():
        trouvees = [c for c in colonnes
                    if any(m in c.lower().replace("é", "e").replace("è", "e")
                           for m in mots)]
        resultat[role] = trouvees
    return resultat


def inventorier(chemin, encodage, separateur, sortie):
    """Tout est lu en texte : à ce stade on observe, on ne convertit pas."""
    df = pd.read_csv(chemin, sep=separateur, encoding=encodage,
                     dtype=str, keep_default_na=False, na_values=[""])

    ecrire = lambda t="": (print(t), sortie.write(t + "\n"))

    ecrire()
    ecrire("=" * 72)
    ecrire("DIMENSIONS")
    ecrire("=" * 72)
    ecrire(f"  {len(df):>8,} lignes".replace(",", " "))
    ecrire(f"  {len(df.columns):>8}   colonnes")

    ecrire()
    ecrire("=" * 72)
    ecrire("COLONNES")
    ecrire("=" * 72)
    ecrire(f"  {'nom':<34} {'rempli':>8} {'distincts':>10}  exemple")
    ecrire("  " + "-" * 68)
    for c in df.columns:
        rempli = df[c].notna().mean()
        distincts = df[c].nunique(dropna=True)
        exemples = df[c].dropna().unique()[:1]
        exemple = str(exemples[0])[:24] if len(exemples) else ""
        ecrire(f"  {c[:34]:<34} {rempli:>7.1%} {distincts:>10}  {exemple}")

    ecrire()
    ecrire("=" * 72)
    ecrire("COLONNES CANDIDATES (heuristique — à valider à l'oeil)")
    ecrire("=" * 72)
    candidates = colonnes_candidates(list(df.columns))
    for role, trouvees in candidates.items():
        marque = "OK  " if trouvees else "RIEN"
        ecrire(f"  [{marque}] {role:<14} {', '.join(trouvees) if trouvees else '-'}")

    ecrire()
    ecrire("=" * 72)
    ecrire("LES QUATRE QUESTIONS")
    ecrire("=" * 72)
    ecrire(f"  1. Colonnes présentes ............. {len(df.columns)} (voir ci-dessus)")
    ecrire(f"  2. Période couverte ............... à lire dans les colonnes de date")
    q3 = "OUI" if candidates["type_marche"] else "NON — test 2 à revoir"
    q4 = "OUI" if candidates["identifiant"] else "NON — rapprochement sur le libellé"
    ecrire(f"  3. Type de marché présent ? ....... {q3}")
    ecrire(f"  4. Identifiant fournisseur ? ...... {q4}")

    ecrire()
    ecrire("=" * 72)
    ecrire("APERÇU — 5 premières lignes")
    ecrire("=" * 72)
    with pd.option_context("display.max_columns", None, "display.width", 200):
        ecrire(df.head(5).to_string())

    return df


def main():
    forcer = "--forcer" in sys.argv
    cfg = charger_config()
    src = cfg["source"]

    url = src.get("url")
    if not url:
        print("ERREUR : aucune URL dans config/params.yaml, section source.url")
        return 1

    chemin = RACINE / src["fichier"]

    print("=" * 72)
    print("TÉLÉCHARGEMENT")
    print("=" * 72)
    telecharger(url, chemin, forcer)

    sha = empreinte(chemin)
    taille = chemin.stat().st_size
    encodage = detecter_encodage(chemin)
    separateur = detecter_separateur(chemin, encodage)

    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as sortie:
        entete = [
            "",
            "=" * 72,
            "FICHIER",
            "=" * 72,
            f"  nom .......... {chemin.name}",
            f"  taille ....... {taille:,} octets".replace(",", " "),
            f"  sha256 ....... {sha}",
            f"  encodage ..... {encodage}",
            f"  séparateur ... {repr(separateur)}",
        ]
        for ligne in entete:
            print(ligne)
            sortie.write(ligne + "\n")

        inventorier(chemin, encodage, separateur, sortie)

    print()
    print(f"Rapport enregistré dans {RAPPORT.relative_to(RACINE)}")
    print()
    print("À REPORTER DANS config/params.yaml, section source :")
    print(f"  encodage: \"{encodage}\"")
    print(f"  separateur: \"{separateur}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
