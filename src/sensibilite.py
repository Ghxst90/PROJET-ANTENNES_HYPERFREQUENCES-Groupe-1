"""
sensibilite.py — Études de sensibilité : on fait varier UN paramètre à la fois.

Responsable : Vouffo (Module G)   Soutien : Tsofack
Dépend de : simulation, metriques, visualisation
Principe : pour chaque valeur du paramètre, relancer la simulation, noter le SINR moyen
et la couverture, puis tracer une courbe avec visualisation.tracer_courbe
(enregistrée dans figures/).

Ordres de grandeur attendus (à vérifier avec vos résultats) :
  - doubler le nombre d'éléments : environ +6 dB quand le trajet via le RIS domine ;
  - phases sur 2 bits : environ -1 dB ; sur 1 bit : environ -4 dB (par rapport au continu).
"""
import numpy as np
from src import config


def etude_nb_elements(liste_n=(16, 64, 256, 1024)):
    """SINR moyen en fonction du nombre d'éléments du RIS.

    Entrées : liste_n (nombres d'éléments à tester)
    Sortie  : (liste_n, liste des SINR moyens en dB) ; enregistre figures/sensibilite_nb_elements.png
    Piste   : adapter n_x et n_y (par exemple carré : n_x = n_y = racine de N).
    """
    raise NotImplementedError("À écrire par Vouffo")


def etude_resolution_phases(bits_liste=(None, 2, 1)):
    """Effet de la résolution des phases (None = continue, 2 bits, 1 bit).

    Entrées : bits_liste
    Sortie  : (bits_liste, SINR moyens en dB) ; enregistre figures/sensibilite_phases.png
    Piste   : optimisation.quantifier_phases
    """
    raise NotImplementedError("À écrire par Vouffo")


def etude_position_ris(positions_ris):
    """Comparaison de la couverture selon la position du RIS.

    Entrées : positions_ris (liste de 3 à 5 positions numpy (x, y, z))
    Sortie  : (positions_ris, taux de couverture pour chacune) ;
              enregistre figures/sensibilite_position.png
    """
    raise NotImplementedError("À écrire par Vouffo")


def etude_nb_utilisateurs(liste_nb=(1, 3, 5, 10)):
    """Évolution du SINR moyen et de la couverture selon le nombre d'utilisateurs.

    Entrées : liste_nb
    Sortie  : (liste_nb, SINR moyens en dB, taux de couverture) ;
              enregistre figures/sensibilite_utilisateurs.png
    À préciser en groupe : comment les utilisateurs se partagent le RIS (une seule
    configuration de phases pour tous ?).
    """
    raise NotImplementedError("À écrire par Vouffo")
