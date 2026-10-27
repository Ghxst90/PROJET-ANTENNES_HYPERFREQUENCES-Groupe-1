"""Tests du module canal_direct (responsable des tests : Vouffo).
Lancer depuis la racine du dépôt :  pytest
Un test qui échoue signale une erreur dans la fonction testée."""
import numpy as np
from src import config
from src.canal_direct import (perte_espace_libre, est_bloque,
                              attenuation_blocage, canal_direct)


def test_perte_1m_39ghz():
    # Valeur attendue : environ 64 dB à 1 m pour 39 GHz
    assert abs(perte_espace_libre(39e9, 1.0) - 64.26) < 0.2


def test_perte_augmente_de_20db_par_decade():
    ecart = perte_espace_libre(39e9, 10.0) - perte_espace_libre(39e9, 1.0)
    assert abs(ecart - 20.0) < 1e-6


def test_perte_plus_forte_a_39ghz_qu_a_3_5ghz():
    # Environ 21 dB de plus à 39 GHz qu'à 3,5 GHz, à distance égale
    ecart = perte_espace_libre(39e9, 1.0) - perte_espace_libre(3.5e9, 1.0)
    assert abs(ecart - 20.94) < 0.1


def test_trajet_bloque_par_immeuble():
    bs = np.array([0.0, 0.0, 10.0])
    ue = np.array([50.0, 0.0, 1.5])
    assert est_bloque(bs, ue, [(20.0, 30.0, -10.0, 10.0)]) is True


def test_trajet_libre_en_visibilite_directe():
    bs = np.array([0.0, 0.0, 10.0])
    ue = np.array([50.0, 40.0, 1.5])
    assert est_bloque(bs, ue, [(20.0, 30.0, -10.0, 10.0)]) is False


def test_attenuation_blocage():
    assert attenuation_blocage(True) == config.ATTENUATION_BLOCAGE_DB
    assert attenuation_blocage(False) == 0.0


def test_amplitude_canal_direct_sans_obstacle():
    bs = np.array([0.0, 0.0, 10.0])
    ue = np.array([10.0, 0.0, 10.0])          # distance exacte : 10 m
    h = canal_direct(bs, ue, 39e9, [])
    attendu = 10 ** (-perte_espace_libre(39e9, 10.0) / 20)
    assert abs(abs(h) - attendu) < 1e-12
