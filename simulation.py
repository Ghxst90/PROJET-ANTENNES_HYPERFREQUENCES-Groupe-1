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
import os
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
    Clés ajoutées : "pos_ue_cible" (utilisateur visé par le RIS, config.POS_UE) et
        "masque_ombre" (tableau booléen (len(y_vals), len(x_vals)), True si le trajet
        direct BS -> UE est bloqué).
    """
    zone = config.ZONE
    x_vals = np.arange(zone["x_min"], zone["x_max"] + 1e-9, zone["pas"])
    y_vals = np.arange(zone["y_min"], zone["y_max"] + 1e-9, zone["pas"])
    pos_elements = canal_ris.positions_elements(
        config.POS_RIS, config.N_X, config.N_Y, config.PAS_ELEMENTS)
    masque_ombre = np.array([
        [canal_direct.est_bloque(config.POS_BS, np.array([x, y, config.HAUTEUR_UE]),
                                 config.OBSTACLES) for x in x_vals]
        for y in y_vals])
    return {"pos_bs": config.POS_BS, "pos_ris": config.POS_RIS,
            "obstacles": config.OBSTACLES, "f_hz": config.F_HZ,
            "x_vals": x_vals, "y_vals": y_vals, "hauteur_ue": config.HAUTEUR_UE,
            "pos_elements": pos_elements,
            "pos_ue_cible": config.POS_UE, "masque_ombre": masque_ombre}


def _quantifier_si_besoin(phases):
    """Applique la résolution de phase de config.BITS_PHASE (None = phases continues)."""
    if config.BITS_PHASE is None:
        return phases
    return optimisation.quantifier_phases(phases, config.BITS_PHASE)


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
    pos_bs, pos_elements = scenario["pos_bs"], scenario["pos_elements"]
    x_vals, y_vals = scenario["x_vals"], scenario["y_vals"]
    f_hz, obstacles = scenario["f_hz"], scenario["obstacles"]

    # Vérification du mode demandé
    if isinstance(phases, str):
        if phases != "analytique":
            raise ValueError("phases doit être None, un tableau (N,) ou 'analytique'")
        mode = "analytique"
    elif phases is None:
        mode = "sans_ris"
    else:
        phases = np.asarray(phases, dtype=float)
        if phases.shape != (len(pos_elements),):
            raise ValueError(f"phases doit avoir {len(pos_elements)} éléments, "
                             f"reçu la forme {phases.shape}")
        mode = "fixe"

    bruit_dbm = metriques.bruit_dbm(config.BANDE_HZ, config.FACTEUR_BRUIT_DB)
    p_tx_dbm = config.P_TX_DBM + config.GAIN_ANTENNES_DB      # gains d'antennes inclus
    g = None if mode == "sans_ris" else canal_ris.canal_bs_ris(pos_bs, pos_elements, f_hz)

    carte = np.empty((len(y_vals), len(x_vals)))
    for i, y in enumerate(y_vals):
        for j, x in enumerate(x_vals):
            pos_ue = np.array([x, y, scenario["hauteur_ue"]])
            h_d = canal_direct.canal_direct(pos_bs, pos_ue, f_hz, obstacles)
            if mode == "sans_ris":
                h = h_d
            else:
                h_r = canal_ris.canal_ris_ue(pos_elements, pos_ue, f_hz)
                if mode == "analytique":
                    phases_pt = _quantifier_si_besoin(
                        optimisation.phases_analytiques(h_d, h_r, g))
                else:
                    phases_pt = phases
                h = canal_ris.canal_total(h_d, h_r, g, phases_pt)
            p_recue_dbm = metriques.puissance_recue_dbm(p_tx_dbm, h)
            carte[i, j] = metriques.sinr_db(p_recue_dbm, bruit_dbm, None)   # None : pas d'interférences
    return carte


def _phases_pour_cible(scenario):
    """Phases analytiques du RIS pour l'utilisateur cible (une seule configuration fixe)."""
    pos_ue = scenario["pos_ue_cible"]
    h_d = canal_direct.canal_direct(scenario["pos_bs"], pos_ue, scenario["f_hz"],
                                    scenario["obstacles"])
    h_r = canal_ris.canal_ris_ue(scenario["pos_elements"], pos_ue, scenario["f_hz"])
    g = canal_ris.canal_bs_ris(scenario["pos_bs"], scenario["pos_elements"], scenario["f_hz"])
    return _quantifier_si_besoin(optimisation.phases_analytiques(h_d, h_r, g))


def lancer_comparaison(scenario):
    """Simule les cas sans RIS et avec RIS, compare, sauvegarde.

    Entrées : scenario
    Sortie  : dictionnaire renvoyé par metriques.comparer_avec_sans_ris (cas sans RIS
              contre cas avec RIS configuré pour l'utilisateur cible), complété par les
              clés "sinr_sans_ris", "sinr_avec_ris", "sinr_borne_analytique" (grilles de
              SINR en dB) et "phases_cible" ;
              enregistre les grilles de SINR dans resultats/cartes_sinr.npz
    """
    phases_cible = _phases_pour_cible(scenario)
    sinr_sans = simuler_grille(scenario, None)
    sinr_avec = simuler_grille(scenario, phases_cible)
    sinr_borne = simuler_grille(scenario, "analytique")

    resultat = dict(metriques.comparer_avec_sans_ris(sinr_sans, sinr_avec))
    resultat.update({"sinr_sans_ris": sinr_sans, "sinr_avec_ris": sinr_avec,
                     "sinr_borne_analytique": sinr_borne, "phases_cible": phases_cible})

    os.makedirs(config.DOSSIER_RESULTATS, exist_ok=True)
    np.savez(os.path.join(config.DOSSIER_RESULTATS, "cartes_sinr.npz"),
             x_vals=scenario["x_vals"], y_vals=scenario["y_vals"],
             masque_ombre=scenario["masque_ombre"], phases_cible=phases_cible,
             sinr_sans_ris=sinr_sans, sinr_avec_ris=sinr_avec,
             sinr_borne_analytique=sinr_borne)
    return resultat


def _enregistrer_cartes(scenario, resultat):
    """Trace les cartes de SINR (sans RIS, avec RIS, borne analytique) dans figures/.
    Version autonome, remplaçable par les fonctions de visualisation.py (Tsala)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    cas = [("Sans RIS", resultat["sinr_sans_ris"]),
           ("RIS configuré pour la cible", resultat["sinr_avec_ris"]),
           ("RIS optimal en chaque point (borne)", resultat["sinr_borne_analytique"])]
    x, y = scenario["x_vals"], scenario["y_vals"]
    fig, axes = plt.subplots(1, 3, figsize=(17, 5), sharey=True)
    for ax, (titre, carte) in zip(axes, cas):
        im = ax.imshow(carte, origin="lower", extent=[x[0], x[-1], y[0], y[-1]],
                       vmin=-10, vmax=60, cmap="viridis", aspect="equal")
        for (x0, x1, y0, y1) in scenario["obstacles"]:
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="red", lw=2))
        ax.plot(*scenario["pos_bs"][:2], "w^", ms=10)
        ax.plot(*scenario["pos_ris"][:2], "ws", ms=9)
        ax.plot(*scenario["pos_ue_cible"][:2], "wx", ms=9)
        ax.set_title(titre, fontsize=10)
        ax.set_xlabel("x (m)")
    axes[0].set_ylabel("y (m)")
    fig.colorbar(im, ax=axes, label="SINR (dB)", shrink=0.8)
    os.makedirs(config.DOSSIER_FIGURES, exist_ok=True)
    chemin = os.path.join(config.DOSSIER_FIGURES, "cartes_sinr.png")
    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return chemin


def main():
    """Lance le scénario par défaut et enregistre les cartes dans figures/."""
    scenario = construire_scenario()
    resultat = lancer_comparaison(scenario)
    print("Comparaison avec / sans RIS :")
    for cle, valeur in resultat.items():
        if not isinstance(valeur, np.ndarray):
            print(f"  {cle} : {valeur}")
    chemin = _enregistrer_cartes(scenario, resultat)
    print(f"Grilles de SINR enregistrées dans {config.DOSSIER_RESULTATS}")
    print(f"Cartes enregistrées dans {chemin}")


if __name__ == "__main__":
    main()
