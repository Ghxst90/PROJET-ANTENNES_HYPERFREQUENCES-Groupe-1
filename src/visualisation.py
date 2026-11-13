"""
visualisation.py — Cartes de couverture et courbes pour le rapport et les slides.

Responsable : Tsala
Utilise : matplotlib. Les images sont enregistrées dans le dossier figures/.
Chaque figure doit avoir : titre, axes nommés avec unités, barre de couleur (cartes).
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")  # pas de fenêtre : on enregistre directement dans un fichier
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from src import config


def _seuil_couverture():
    """Seuil de couverture en dB (config.SEUIL_COUVERTURE_DB), ou None s'il n'est pas défini."""
    return getattr(config, "SEUIL_COUVERTURE_DB", None)


def _preparer_fichier(fichier):
    """Crée le dossier de destination s'il n'existe pas.

    Entrée : fichier (chemin, ex. "figures/carte_sans_ris.png")
    Sortie : objet Path
    """
    chemin = Path(fichier)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    return chemin


def _verifier_grille(grille, x_vals, y_vals):
    """Vérifie que la grille a la forme (len(y_vals), len(x_vals)) et la renvoie en float.

    Entrées : grille (tableau 2D), x_vals, y_vals (positions en m)
    Sortie  : tableau numpy 2D de réels
    """
    grille = np.asarray(grille, dtype=float)
    if grille.shape != (len(y_vals), len(x_vals)):
        raise ValueError(
            f"La grille doit avoir la forme (len(y_vals), len(x_vals)) = "
            f"({len(y_vals)}, {len(x_vals)}), reçu {grille.shape}"
        )
    return grille


def _bornes_couleur(*grilles):
    """Bornes (min, max) de l'échelle de couleur, en ignorant les valeurs infinies ou NaN.

    Entrées : une ou plusieurs grilles de SINR (dB)
    Sortie  : (vmin, vmax)
    """
    valeurs = np.concatenate([g[np.isfinite(g)].ravel() for g in grilles])
    return valeurs.min(), valeurs.max()


def _dessiner_obstacles(axe, obstacles):
    """Dessine les obstacles en rectangles gris.

    FORMAT SUPPOSÉ d'un obstacle : (x_min, y_min, largeur, hauteur) en m, vue de dessus.
    Si config.OBSTACLES utilise un autre format, c'est la seule fonction à adapter.

    Entrées : axe (axes matplotlib), obstacles (liste de rectangles, ou None)
    Sortie  : aucune
    """
    for i, (x_min, y_min, largeur, hauteur) in enumerate(obstacles or []):
        axe.add_patch(Rectangle((x_min, y_min), largeur, hauteur, facecolor="gray",
                                edgecolor="black", alpha=0.85, zorder=2,
                                label="Obstacle" if i == 0 else None))


def _dessiner_carte(axe, grille, x_vals, y_vals, pos_bs, pos_ris, obstacles, vmin, vmax):
    """Dessine une carte de SINR complète sur un axe et renvoie l'image (pour la barre de couleur).

    Entrées : axe, grille (len(y_vals), len(x_vals)) en dB, x_vals, y_vals (m),
              pos_bs, pos_ris (numpy (x, y, z) ou None), obstacles, vmin / vmax (dB)
    Sortie  : objet image matplotlib
    """
    image = axe.pcolormesh(x_vals, y_vals, grille, shading="nearest",
                           cmap="viridis", vmin=vmin, vmax=vmax)
    seuil = _seuil_couverture()
    finies = grille[np.isfinite(grille)]
    if seuil is not None and finies.min() < seuil < finies.max():
        axe.contour(x_vals, y_vals, grille, levels=[seuil], colors="white",
                    linewidths=1.5, linestyles="--")
        axe.plot([], [], "--", color="white", label=f"Seuil {seuil:g} dB")
    _dessiner_obstacles(axe, obstacles)
    if pos_bs is not None:
        axe.scatter(pos_bs[0], pos_bs[1], marker="^", s=140, c="white", edgecolors="black",
                    linewidths=1.2, label="BS", zorder=3)
    if pos_ris is not None:
        axe.scatter(pos_ris[0], pos_ris[1], marker="s", s=140, c="orange", edgecolors="black",
                    linewidths=1.2, label="RIS", zorder=3)
    axe.set_xlabel("x (m)")
    axe.set_ylabel("y (m)")
    axe.set_aspect("equal")
    axe.legend(loc="upper right", framealpha=0.9, fontsize=8)
    return image


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
    grille = _verifier_grille(grille_sinr_db, x_vals, y_vals)
    chemin = _preparer_fichier(fichier)
    vmin, vmax = _bornes_couleur(grille)
    figure, axe = plt.subplots(figsize=(7, 5.5))
    image = _dessiner_carte(axe, grille, x_vals, y_vals, pos_bs, pos_ris, obstacles, vmin, vmax)
    figure.colorbar(image, ax=axe, label="SINR (dB)")
    axe.set_title(titre)
    figure.savefig(chemin, dpi=200, bbox_inches="tight")
    plt.close(figure)


def carte_comparaison(grille_sans, grille_avec, x_vals, y_vals, pos_bs, pos_ris,
                      obstacles, fichier):
    """Deux cartes côte à côte (sans RIS / avec RIS) avec la même échelle de couleurs.

    Entrées : voir carte_sinr ; grille_sans et grille_avec ont la même forme.
    Sortie  : aucune ; enregistre l'image dans `fichier`.
    """
    sans = _verifier_grille(grille_sans, x_vals, y_vals)
    avec = _verifier_grille(grille_avec, x_vals, y_vals)
    chemin = _preparer_fichier(fichier)
    vmin, vmax = _bornes_couleur(sans, avec)
    seuil = _seuil_couverture()

    figure, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    for axe, grille, nom, ris in [(axes[0], sans, "Sans RIS", None),
                                  (axes[1], avec, "Avec RIS", pos_ris)]:
        # le RIS n'est dessiné que sur la carte "Avec RIS"
        image = _dessiner_carte(axe, grille, x_vals, y_vals, pos_bs, ris, obstacles, vmin, vmax)
        titre = nom
        if seuil is not None:
            titre += f" — couverture {100 * np.mean(grille >= seuil):.0f} % (seuil {seuil:g} dB)"
        axe.set_title(titre)
    axes[1].set_ylabel("")
    figure.colorbar(image, ax=axes, label="SINR (dB)", shrink=0.9)
    figure.savefig(chemin, dpi=200, bbox_inches="tight")
    plt.close(figure)


def tracer_courbe(x, y, titre, label_x, label_y, fichier, label_serie=None):
    """Courbe simple, utilisée par sensibilite.py.

    Entrées : x, y (listes ou tableaux), titre, label_x et label_y (avec unités),
              fichier (chemin d'enregistrement), label_serie (légende, optionnel)
    Sortie  : aucune ; enregistre l'image.
    """
    chemin = _preparer_fichier(fichier)
    figure, axe = plt.subplots(figsize=(7, 4.5))
    axe.plot(x, y, marker="o", linewidth=2, label=label_serie)
    axe.set_xlabel(label_x)
    axe.set_ylabel(label_y)
    axe.set_title(titre)
    axe.grid(True, alpha=0.3)
    if label_serie is not None:
        axe.legend()
    figure.savefig(chemin, dpi=200, bbox_inches="tight")
    plt.close(figure)