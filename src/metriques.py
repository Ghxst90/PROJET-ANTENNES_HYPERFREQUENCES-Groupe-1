"""
metriques.py — Indicateurs de performance : puissance reçue, SINR, couverture, débit.

Responsable : Aissatou (Module F)
Utilisé par : optimisation.py (SINR), simulation.py, sensibilite.py

Unités : puissances en dBm, SINR en dB, bande en Hz, débit en bit/s.
Attention : les sommes de puissances se font en échelle LINÉAIRE (mW), pas en dB.
"""
import numpy as np
from src import config


def puissance_recue_dbm(p_tx_dbm, h):
    """Puissance reçue en dBm.

    Entrées : p_tx_dbm (dBm), h (coefficient de canal complexe, ou tableau de coefficients)
    Sortie  : p_rx en dBm = p_tx_dbm + 20 * log10(|h|)
    """
    return p_tx_dbm + 20 * np.log10(np.abs(h))


def bruit_dbm(bande_hz=config.BANDE_HZ, facteur_bruit_db=config.FACTEUR_BRUIT_DB):
    """Puissance de bruit thermique en dBm.

    Entrées : bande_hz (Hz), facteur_bruit_db (dB)
    Sortie  : -174 + 10 * log10(bande_hz) + facteur_bruit_db
    Exemple : 100 MHz et 7 dB donnent -87 dBm.
    """
    return -174 + 10 * np.log10(bande_hz) + facteur_bruit_db


def sinr_db(p_rx_dbm, bruit_dbm_val, interferences_dbm=None):
    """SINR en dB (rapport signal sur bruit plus interférences).

    Entrées : p_rx_dbm, bruit_dbm_val (dBm), interferences_dbm (dBm ou None)
    Sortie  : SINR en dB
        Convertir en mW (10**(x/10)), additionner bruit et interférences,
        puis SINR = 10 * log10(P_signal / (bruit + interférences)).
    Sans interférences, SINR = p_rx_dbm - bruit_dbm_val.
    Doit fonctionner aussi avec des tableaux numpy (cartes de couverture).
    """
    bruit_mw = 10 ** (np.asarray(bruit_dbm_val) / 10)
    if interferences_dbm is not None:
        bruit_mw = bruit_mw + 10 ** (np.asarray(interferences_dbm) / 10)
    return np.asarray(p_rx_dbm) - 10 * np.log10(bruit_mw)


def debit_shannon(sinr_db_val, bande_hz=config.BANDE_HZ):
    """Débit maximal estimé (capacité de Shannon).

    Entrées : sinr_db_val (dB), bande_hz (Hz)
    Sortie  : B * log2(1 + SINR_linéaire) en bit/s
    Exemple : SINR = 0 dB et B = 1 MHz donnent 1e6 bit/s.
    """
    sinr_lin = 10 ** (np.asarray(sinr_db_val) / 10)
    return bande_hz * np.log2(1 + sinr_lin)


def taux_couverture(grille_sinr_db, seuil_db=config.SEUIL_COUVERTURE_DB):
    """Proportion de la zone où le SINR atteint le seuil.

    Entrées : grille_sinr_db (tableau numpy de SINR en dB), seuil_db (dB)
    Sortie  : nombre entre 0 et 1 (un point est couvert si SINR >= seuil)
    """
    return float(np.mean(np.asarray(grille_sinr_db) >= seuil_db))


def comparer_avec_sans_ris(grille_sans, grille_avec,
                           seuil_db=config.SEUIL_COUVERTURE_DB,
                           bande_hz=config.BANDE_HZ):
    """Compare les performances sans RIS et avec RIS.

    Entrées : grille_sans, grille_avec (tableaux de SINR en dB de même forme)
    Sortie  : dictionnaire avec les clés
        "sinr_moyen_sans_db", "sinr_moyen_avec_db",
        "couverture_sans", "couverture_avec",
        "debit_moyen_sans", "debit_moyen_avec"
    Le SINR moyen est la moyenne des valeurs en dB (à préciser dans le rapport).
    """
    sans = np.asarray(grille_sans)
    avec = np.asarray(grille_avec)
    return {
        "sinr_moyen_sans_db": float(np.mean(sans)),
        "sinr_moyen_avec_db": float(np.mean(avec)),
        "couverture_sans": taux_couverture(sans, seuil_db),
        "couverture_avec": taux_couverture(avec, seuil_db),
        "debit_moyen_sans": float(np.mean(debit_shannon(sans, bande_hz))),
        "debit_moyen_avec": float(np.mean(debit_shannon(avec, bande_hz))),
    }
