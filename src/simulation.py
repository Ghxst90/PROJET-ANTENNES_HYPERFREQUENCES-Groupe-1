"""
simulation.py — Fichier principal : assemble les modules et calcule les cartes de SINR.

Responsable : Tsofack (Module E)
Dépend de : config, canal_direct, canal_ris, optimisation, metriques
Lancement : python -m src.simulation   (depuis la racine du dépôt)

Schéma d'une simulation :
  1. construire_scenario()           positions, obstacles, grille d'utilisateurs, éléments du RIS
  2. simuler_grille(scenario, ...)   pour chaque point de la grille : canaux, puissance, SINR
  3. lancer_comparaison(scenario)    carte sans RIS, carte avec RIS, comparaison, sauvegarde
"""
import numpy as np
from src import config
from src import canal_direct
from src import canal_ris
from src import optimisation
from src import metriques


def construire_scenario():
    """Construit le scénario à partir de config.py.

    Entrées : aucune
    Sortie  : dictionnaire avec au minimum les clés
        "pos_bs", "pos_ris", "obstacles", "f_hz",
        "x_vals", "y_vals"      (positions de la grille, en m, d'après config.ZONE),
        "hauteur_ue",
        "pos_elements"          (positions des éléments du RIS, tableau (N, 3))
    """
    raise NotImplementedError("À écrire par Tsofack")


def simuler_grille(scenario, phases=None):
    """Calcule le SINR en dB en chaque point de la grille d'utilisateurs.

    Entrées : scenario (voir construire_scenario),
              phases :
                - None         -> SANS RIS (trajet direct seul)
                - tableau (N,) -> RIS avec UNE configuration fixe de phases
                - "analytique" -> RIS avec les phases optimales recalculées en chaque
                                  point (optimisation.phases_analytiques) : borne haute
    Sortie  : tableau 2D de forme (len(y_vals), len(x_vals)), SINR en dB
    """
    raise NotImplementedError("À écrire par Tsofack")


def lancer_comparaison(scenario):
    """Simule les cas sans RIS et avec RIS, compare, sauvegarde.

    Entrées : scenario
    Sortie  : dictionnaire renvoyé par metriques.comparer_avec_sans_ris ;
              enregistre les grilles de SINR dans resultats/ (fichiers .npz ou .csv)
    """
    raise NotImplementedError("À écrire par Tsofack")


def main():
    """Lance le scénario par défaut et enregistre les cartes dans figures/."""
    raise NotImplementedError("À écrire par Tsofack")


if __name__ == "__main__":
    main()
