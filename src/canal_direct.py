"""
canal_direct.py — Canal direct entre la station de base (BS) et l'utilisateur (UE).

Responsable : Aroung (Module B)   Soutien : Tsala
Utilisé par : canal_ris.py (perte_espace_libre), simulation.py

Unités : fréquence en Hz, distances en m, pertes en dB.
"""
import numpy as np
from src import config


def perte_espace_libre(f_hz, d_m):
    """Perte en espace libre (Friis) entre deux points distants de d_m.

    Entrées : f_hz (Hz), d_m (m, > 0)
    Sortie  : perte en dB (nombre positif)

    Formule : PL = 20 * log10(4 * pi * d * f / c)
    Vérification : environ 64 dB à 1 m pour 39 GHz (voir tests/test_canal_direct.py).
    """
    raise NotImplementedError("À écrire par Aroung")


def est_bloque(pos_bs, pos_ue, obstacles):
    """Indique si le trajet direct BS -> UE est coupé par un obstacle (NLOS).

    Entrées : pos_bs, pos_ue (tableaux numpy (x, y, z)),
              obstacles : liste de rectangles (x_min, x_max, y_min, y_max)
    Sortie  : True si le segment BS-UE (vu de dessus, en x et y) traverse
              au moins un rectangle, False sinon (LOS).

    Piste : tester l'intersection d'un segment avec un rectangle (méthode
    de Liang-Barsky), ou échantillonner des points le long du segment.
    """
    raise NotImplementedError("À écrire par Aroung")


def attenuation_blocage(bloque, valeur_db=config.ATTENUATION_BLOCAGE_DB):
    """Atténuation supplémentaire due au blocage.

    Entrées : bloque (bool), valeur_db (dB, réglable)
    Sortie  : valeur_db si bloque, 0.0 sinon
    """
    raise NotImplementedError("À écrire par Aroung")


def canal_direct(pos_bs, pos_ue, f_hz, obstacles):
    """Coefficient complexe h_d du canal direct BS -> UE.

    Entrées : pos_bs, pos_ue (numpy (x, y, z)), f_hz (Hz), obstacles (voir est_bloque)
    Sortie  : nombre complexe h_d

    Modèle :
        d   = distance BS-UE
        PL  = perte_espace_libre(f_hz, d) + attenuation_blocage(est_bloque(...))
        h_d = 10**(-PL/20) * exp(-1j * 2*pi * d / lambda)
    Le module donne l'amplitude, l'exponentielle donne la phase de propagation.
    """
    raise NotImplementedError("À écrire par Aroung")
