"""
canal_ris.py — RIS et canal réfléchi BS -> RIS -> UE.

Responsable : Tsala (Module C)   Soutien : Tsofack
Dépend de : canal_direct.perte_espace_libre
Utilisé par : optimisation.py, simulation.py

CONVENTION RETENUE (à respecter partout, y compris dans le rapport) :
  - g   : canal physique BS -> éléments du RIS, vecteur complexe de taille N
  - h_r : canal physique éléments du RIS -> UE, vecteur complexe de taille N
          (PAS de conjugaison : on garde la phase de propagation exp(-j*2*pi*d/lambda))
  - Signal total : h = h_d + somme_n [ h_r[n] * beta * exp(j*theta[n]) * g[n] ]
  Cela correspond à h_r^T . Theta . g (transposée). La notation h_r^H utilisée dans
  le plan de travail vient d'une autre convention de définition de h_r : à harmoniser
  dans le rapport.
  - Les éléments sont isotropes (pas de diagramme de rayonnement des éléments).

Unités : fréquence en Hz, distances en m, phases en radians.
"""
import numpy as np
from src import config
from src.canal_direct import perte_espace_libre


def positions_elements(centre, n_x, n_y, pas):
    """Positions des n_x * n_y éléments du RIS.

    Entrées : centre (numpy (x, y, z)), n_x (éléments selon y), n_y (éléments selon z),
              pas (m, espacement, en général lambda/2)
    Sortie  : tableau numpy de forme (N, 3), N = n_x * n_y

    Le panneau est vertical, dans le plan x = centre[0] : y varie avec n_x, z avec n_y.
    Les éléments sont centrés autour de `centre`.
    """
    raise NotImplementedError("À écrire par Tsala")


def canal_bs_ris(pos_bs, pos_elements, f_hz):
    """Canal g entre la BS et chaque élément du RIS.

    Entrées : pos_bs (numpy (x, y, z)), pos_elements (N, 3), f_hz (Hz)
    Sortie  : vecteur complexe g de taille N

    Pour chaque élément n, avec d_n la distance BS-élément :
        g[n] = 10**(-PL(d_n)/20) * exp(-1j * 2*pi * d_n / lambda)
    """
    raise NotImplementedError("À écrire par Tsala")


def canal_ris_ue(pos_elements, pos_ue, f_hz):
    """Canal h_r entre chaque élément du RIS et l'UE (même formule que g, côté UE).

    Entrées : pos_elements (N, 3), pos_ue (numpy (x, y, z)), f_hz (Hz)
    Sortie  : vecteur complexe h_r de taille N
    """
    raise NotImplementedError("À écrire par Tsala")


def matrice_reflexion(phases, amplitude=config.AMPLITUDE_RIS):
    """Matrice de réflexion Theta du RIS.

    Entrées : phases (vecteur de N angles en rad), amplitude (module beta, 1 par défaut)
    Sortie  : matrice diagonale N x N, Theta[n, n] = amplitude * exp(1j * phases[n])
    """
    raise NotImplementedError("À écrire par Tsala")


def canal_total(h_d, h_r, g, phases, amplitude=config.AMPLITUDE_RIS):
    """Coefficient complexe total vu par l'UE : trajet direct + trajet via le RIS.

    Entrées : h_d (complexe), h_r et g (vecteurs complexes de taille N),
              phases (N angles en rad), amplitude (module beta)
    Sortie  : nombre complexe
        h = h_d + somme_n [ h_r[n] * amplitude * exp(1j*phases[n]) * g[n] ]
    """
    raise NotImplementedError("À écrire par Tsala")
