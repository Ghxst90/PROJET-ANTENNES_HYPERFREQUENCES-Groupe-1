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
    return 20 * np.log10(4 * np.pi * d_m * f_hz / config.C)


def est_bloque(pos_bs, pos_ue, obstacles):
    """Indique si le trajet direct BS -> UE est coupé par un obstacle (NLOS).

    Entrées : pos_bs, pos_ue (tableaux numpy (x, y, z)),
              obstacles : liste de rectangles (x_min, x_max, y_min, y_max)
    Sortie  : True si le segment BS-UE (vu de dessus, en x et y) traverse
              au moins un rectangle, False sinon (LOS).

    Piste : tester l'intersection d'un segment avec un rectangle (méthode
    de Liang-Barsky), ou échantillonner des points le long du segment.
    """
    # Méthode de Liang-Barsky : on découpe le segment BS-UE (vu de dessus) par chaque rectangle.
    x0, y0 = pos_bs[0], pos_bs[1]
    dx = pos_ue[0] - x0
    dy = pos_ue[1] - y0
    for (x_min, x_max, y_min, y_max) in obstacles:
        t_entree, t_sortie = 0.0, 1.0      # paramètre t le long du segment (0 = BS, 1 = UE)
        traverse = True
        # Pour chaque bord du rectangle : (p, q) tels que le point est dedans si p*t <= q
        for p, q in ((-dx, x0 - x_min), (dx, x_max - x0),
                     (-dy, y0 - y_min), (dy, y_max - y0)):
            if p == 0:                      # segment parallèle à ce bord
                if q < 0:                   # et à l'extérieur du rectangle
                    traverse = False
                    break
            else:
                r = q / p
                if p < 0:                   # le segment entre par ce bord
                    if r > t_sortie:
                        traverse = False
                        break
                    t_entree = max(t_entree, r)
                else:                       # le segment sort par ce bord
                    if r < t_entree:
                        traverse = False
                        break
                    t_sortie = min(t_sortie, r)
        if traverse:
            return True
    return False


def attenuation_blocage(bloque, valeur_db=config.ATTENUATION_BLOCAGE_DB):
    """Atténuation supplémentaire due au blocage.

    Entrées : bloque (bool), valeur_db (dB, réglable)
    Sortie  : valeur_db si bloque, 0.0 sinon
    """
    return valeur_db if bloque else 0.0


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
    d = np.linalg.norm(np.asarray(pos_ue) - np.asarray(pos_bs))
    perte_db = perte_espace_libre(f_hz, d) + attenuation_blocage(est_bloque(pos_bs, pos_ue, obstacles))
    amplitude = 10 ** (-perte_db / 20)                 # amplitude linéaire (pas en dB)
    phase = -2 * np.pi * d / config.LAMBDA             # phase de propagation
    return amplitude * np.exp(1j * phase)


def canal_direct_grille(pos_bs, positions_ue, f_hz, obstacles):
    """Version « grille » de canal_direct : un coefficient h_d par point.

    Entrées : pos_bs (numpy (x, y, z)), positions_ue (tableau de forme (M, 3)),
              f_hz (Hz), obstacles (voir est_bloque)
    Sortie  : tableau complexe de taille M (un h_d par point de la grille)
    """
    return np.array([canal_direct(pos_bs, p, f_hz, obstacles) for p in positions_ue])