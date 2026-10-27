"""Tests du module metriques (responsable des tests : Vouffo)."""
import numpy as np
from src import config
from src.metriques import (puissance_recue_dbm, bruit_dbm, sinr_db, debit_shannon,
                           taux_couverture, comparer_avec_sans_ris)


def test_puissance_recue():
    assert abs(puissance_recue_dbm(30.0, 1e-3) - (-30.0)) < 1e-9


def test_bruit_100mhz_7db():
    assert abs(bruit_dbm(100e6, 7.0) - (-87.0)) < 0.05


def test_sinr_sans_interferences():
    assert abs(sinr_db(-60.0, -87.0) - 27.0) < 1e-9


def test_sinr_avec_interferences_egales_au_bruit():
    # bruit + interférences = 2 fois le bruit, donc SINR baisse d'environ 3 dB
    sans = sinr_db(-60.0, -87.0)
    avec = sinr_db(-60.0, -87.0, interferences_dbm=-87.0)
    assert abs((sans - avec) - 3.01) < 0.01


def test_sinr_fonctionne_sur_tableau():
    p = np.array([[-60.0, -70.0], [-80.0, -90.0]])
    assert sinr_db(p, -87.0).shape == (2, 2)


def test_debit_shannon():
    assert abs(debit_shannon(0.0, 1e6) - 1e6) < 1e-6
    assert debit_shannon(20.0, 1e6) > debit_shannon(10.0, 1e6)


def test_taux_couverture():
    grille = np.array([[0.0, 5.0], [10.0, 15.0]])
    assert abs(taux_couverture(grille, 10.0) - 0.5) < 1e-12


def test_taux_couverture_entre_0_et_1():
    grille = np.random.default_rng(0).uniform(-20, 40, (20, 20))
    assert 0.0 <= taux_couverture(grille, config.SEUIL_COUVERTURE_DB) <= 1.0


def test_comparaison_cles_et_sens():
    sans = np.full((5, 5), 0.0)
    avec = np.full((5, 5), 20.0)
    res = comparer_avec_sans_ris(sans, avec, seuil_db=10.0, bande_hz=1e6)
    for cle in ["sinr_moyen_sans_db", "sinr_moyen_avec_db", "couverture_sans",
                "couverture_avec", "debit_moyen_sans", "debit_moyen_avec"]:
        assert cle in res
    assert res["sinr_moyen_avec_db"] > res["sinr_moyen_sans_db"]
    assert res["couverture_avec"] > res["couverture_sans"]
