"""
visualisation.py — Cartes de couverture et courbes pour le rapport et les slides.

Responsable : Tsala
Utilise : matplotlib. Les images sont enregistrées dans le dossier figures/.
Chaque figure doit avoir : titre, axes nommés avec unités, barre de couleur (cartes).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")  # pas de fenêtre : on enregistre directement dans un fichier
import matplotlib.pyplot as plt
from src import config


def carte_sinr(grille_sinr_db, x_vals, y_vals, pos_bs, pos_ris, obstacles,
               titre, fichier):
    """Carte de couverture (heatmap) du SINR.

    Entrées : grille_sinr_db (tableau 2D de forme (len(y_vals), len(x_vals))),
              x_vals, y_vals (positions de la grille en m),
              pos_bs, pos_ris (numpy (x, y, z)), obstacles (rectangles),
              titre (str), fichier (chemin, ex. "figures/carte_sans_ris.png")
    Sortie  : aucune ; enregistre l'image.
    À montrer : BS, RIS, obstacles (rectangles gris), barre de couleur en dB,
    éventuellement le contour du seuil de couverture (config.SEUIL_COUVERTURE_DB).
    """
    raise NotImplementedError("À écrire par Tsala")


def carte_comparaison(grille_sans, grille_avec, x_vals, y_vals, pos_bs, pos_ris,
                      obstacles, fichier):
    """Deux cartes côte à côte (sans RIS / avec RIS) avec la même échelle de couleurs.

    Entrées : voir carte_sinr ; grille_sans et grille_avec ont la même forme.
    Sortie  : aucune ; enregistre l'image dans `fichier`.
    """
    raise NotImplementedError("À écrire par Tsala")


def tracer_courbe(x, y, titre, label_x, label_y, fichier, label_serie=None):
    """Courbe simple, utilisée par sensibilite.py.

    Entrées : x, y (listes ou tableaux), titre, label_x et label_y (avec unités),
              fichier (chemin d'enregistrement), label_serie (légende, optionnel)
    Sortie  : aucune ; enregistre l'image.
    """
    raise NotImplementedError("À écrire par Tsala")
