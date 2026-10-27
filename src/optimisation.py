"""
optimisation.py — Choix des phases du RIS qui maximisent la qualité de réception.

Responsable : Aroung (Module D)   Soutien : Tsofack
Dépend de : metriques (SINR), canal_ris (canal total)
Utilisé par : simulation.py, sensibilite.py, tests/test_optimisation.py

Unités : phases en radians.
"""
import numpy as np
from src import config
from src import metriques
from src import canal_ris


def phases_analytiques(h_d, h_r, g):
    """Solution optimale pour UN utilisateur : tous les trajets s'additionnent en phase.

    Entrées : h_d (complexe), h_r et g (vecteurs complexes de taille N)
    Sortie  : vecteur de N phases en rad, dans [0, 2*pi[
        theta[n] = arg(h_d) - arg(h_r[n] * g[n])
    Avec ces phases, |h| = |h_d| + somme_n |h_r[n] * g[n]| (amplitudes qui s'ajoutent).
    Sert de RÉFÉRENCE pour valider les algorithmes heuristiques.
    """
    raise NotImplementedError("À écrire par Aroung")


def quantifier_phases(phases, bits):
    """Arrondit les phases aux 2**bits valeurs permises par le matériel.

    Entrées : phases (rad), bits (1, 2, ...)
    Sortie  : phases arrondies au multiple de 2*pi / 2**bits le plus proche
    Ordre de grandeur attendu : environ -4 dB de gain avec 1 bit, -1 dB avec 2 bits.
    """
    raise NotImplementedError("À écrire par Aroung")


def fonction_objectif(phases, h_d, h_r, g, interferences_dbm=None):
    """Critère à MAXIMISER : SINR (dB) pour un utilisateur, avec ces phases.

    Entrées : phases (N rad), h_d, h_r, g (voir ci-dessus), interferences_dbm (ou None)
    Sortie  : SINR en dB, calculé avec canal_ris.canal_total puis metriques.puissance_recue_dbm,
              metriques.bruit_dbm et metriques.sinr_db (paramètres pris dans config.py)
    """
    raise NotImplementedError("À écrire par Aroung")


def optimiser_genetique(h_d, h_r, g, taille_population=50, n_iterations=100,
                        bits=config.BITS_PHASE, graine=None):
    """Algorithme génétique pour trouver de bonnes phases.

    Entrées : h_d, h_r, g ; taille_population ; n_iterations ;
              bits (None = phases continues) ; graine (pour reproduire les résultats)
    Sortie  : (meilleures_phases, historique)
              historique = liste du meilleur SINR (dB) à chaque itération
    Étapes classiques : population aléatoire, évaluation, sélection, croisement,
    mutation, répétition.
    """
    raise NotImplementedError("À écrire par Aroung")


def optimiser_pso(h_d, h_r, g, n_particules=30, n_iterations=100,
                  bits=config.BITS_PHASE, graine=None):
    """Essaim de particules (optionnel : à faire si le temps le permet).

    Mêmes entrées et sorties que optimiser_genetique.
    """
    raise NotImplementedError("À écrire par Aroung (optionnel)")
