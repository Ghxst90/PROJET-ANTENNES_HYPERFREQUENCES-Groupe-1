"""Fichier principal : assemble les modules, calcule une carte de SINR sur une grille
de positions et sauvegarde les résultats dans resultats/ (Module E, Tsofack).

Lancer depuis la racine du dépôt :  python -m src.simulation
"""
import csv
import os
import numpy as np

from src import config
from src import canal_direct
from src import canal_ris
from src import optimisation
from src import metriques


def construire_scenario():
    """Construit le scénario à partir de config.py.

    Entrées : aucune (lit config.py).
    Sortie : dictionnaire avec pos_bs, pos_ris, pos_ue_cible, obstacles, positions_elements
    (N,3), xs, ys (axes de la grille), grille_ue (K,3) et masque_ombre (K,) booléen
    (True si le trajet direct BS -> UE est bloqué). Unités : mètres.
    """
    positions_elements = canal_ris.positions_elements(
        config.POS_RIS, config.N_X, config.N_Y, config.PAS_ELEMENTS)
    xs = np.arange(config.ZONE["x_min"], config.ZONE["x_max"] + 1e-9, config.ZONE["pas"])
    ys = np.arange(config.ZONE["y_min"], config.ZONE["y_max"] + 1e-9, config.ZONE["pas"])
    X, Y = np.meshgrid(xs, ys)
    grille_ue = np.column_stack([X.ravel(), Y.ravel(), np.full(X.size, config.HAUTEUR_UE)])
    masque_ombre = np.array([canal_direct.est_bloque(config.POS_BS, p, config.OBSTACLES)
                             for p in grille_ue])
    return {"pos_bs": config.POS_BS, "pos_ris": config.POS_RIS,
            "pos_ue_cible": config.POS_UE, "obstacles": config.OBSTACLES,
            "positions_elements": positions_elements, "xs": xs, "ys": ys,
            "grille_ue": grille_ue, "masque_ombre": masque_ombre}


def simuler_grille(scenario, phases=None):
    """Calcule la carte de SINR sur toute la grille.

    Entrées : scenario (de construire_scenario) ; phases : phases du RIS en radians
    (tableau de taille N) ou None pour le cas sans RIS.
    Sortie : tableau 2D (len(ys), len(xs)) des SINR en dB.
    """
    pos_bs, elements = scenario["pos_bs"], scenario["positions_elements"]
    bruit = metriques.bruit_dbm(config.BANDE_HZ, config.FACTEUR_BRUIT_DB)
    p_tx = config.P_TX_DBM + config.GAIN_ANTENNES_DB
    g = None if phases is None else canal_ris.canal_bs_ris(pos_bs, elements, config.F_HZ)
    sinr = np.empty(len(scenario["grille_ue"]))
    for k, pos_ue in enumerate(scenario["grille_ue"]):
        hd = canal_direct.canal_direct(pos_bs, pos_ue, config.F_HZ, scenario["obstacles"])
        if phases is None:
            h = hd
        else:
            hr = canal_ris.canal_ris_ue(elements, pos_ue, config.F_HZ)
            h = canal_ris.canal_total(hd, hr, g, phases)
        p_recue = metriques.puissance_recue_dbm(p_tx, h)
        sinr[k] = metriques.sinr_db(p_recue, bruit, None)      # None = pas d'interférences
    return sinr.reshape(len(scenario["ys"]), len(scenario["xs"]))


def _phases_cible(scenario):
    """Phases analytiques du RIS pour l'utilisateur cible (solution de référence)."""
    pos_ue = scenario["pos_ue_cible"]
    hd = canal_direct.canal_direct(scenario["pos_bs"], pos_ue, config.F_HZ, scenario["obstacles"])
    hr = canal_ris.canal_ris_ue(scenario["positions_elements"], pos_ue, config.F_HZ)
    g = canal_ris.canal_bs_ris(scenario["pos_bs"], scenario["positions_elements"], config.F_HZ)
    phases = optimisation.phases_analytiques(hd, hr, g)
    if config.BITS_PHASE is not None:
        phases = optimisation.quantifier_phases(phases, config.BITS_PHASE)
    return phases


def lancer_comparaison(scenario):
    """Simule les cas sans RIS et avec RIS (focalisé sur l'utilisateur cible), puis
    enregistre cartes et tableau comparatif dans resultats/.

    Entrée : scenario. Sortie : dictionnaire {sinr_sans_ris, sinr_avec_ris, phases, tableau}.
    Fichiers : resultats/cartes_sinr.npz et resultats/comparaison.csv.
    """
    os.makedirs(config.DOSSIER_RESULTATS, exist_ok=True)
    phases = _phases_cible(scenario)
    cartes = {"sans RIS": simuler_grille(scenario, None),
              "avec RIS": simuler_grille(scenario, phases)}
    ombre = scenario["masque_ombre"].reshape(len(scenario["ys"]), len(scenario["xs"]))

    tableau = []
    for nom, carte in cartes.items():
        debit = metriques.debit_shannon(carte[ombre], config.BANDE_HZ) / 1e6   # Mbit/s
        tableau.append([nom, float(carte.mean()),
                        metriques.taux_couverture(carte, config.SEUIL_COUVERTURE_DB),
                        metriques.taux_couverture(carte[ombre], config.SEUIL_COUVERTURE_DB),
                        float(np.mean(debit))])

    np.savez(os.path.join(config.DOSSIER_RESULTATS, "cartes_sinr.npz"),
             xs=scenario["xs"], ys=scenario["ys"], masque_ombre=ombre, phases=phases,
             sinr_sans_ris=cartes["sans RIS"], sinr_avec_ris=cartes["avec RIS"])
    with open(os.path.join(config.DOSSIER_RESULTATS, "comparaison.csv"), "w", newline="") as f:
        ecr = csv.writer(f)
        ecr.writerow(["cas", "sinr_moyen_db", "couverture_globale", "couverture_ombre",
                      "debit_moyen_ombre_mbps"])
        ecr.writerows([[l[0]] + [f"{v:.4f}" for v in l[1:]] for l in tableau])
    return {"sinr_sans_ris": cartes["sans RIS"], "sinr_avec_ris": cartes["avec RIS"],
            "phases": phases, "tableau": tableau}


def main():
    """Lance le scénario par défaut et affiche le tableau comparatif."""
    scenario = construire_scenario()
    res = lancer_comparaison(scenario)
    print(f"{'Cas':<10}{'SINR moy. (dB)':>16}{'Couv. globale':>15}{'Couv. ombre':>13}{'Débit ombre (Mb/s)':>20}")
    for nom, sinr_moy, couv, couv_ombre, debit in res["tableau"]:
        print(f"{nom:<10}{sinr_moy:>16.1f}{couv:>15.1%}{couv_ombre:>13.1%}{debit:>20.1f}")
    print("Résultats enregistrés dans resultats/")


if __name__ == "__main__":
    main()
