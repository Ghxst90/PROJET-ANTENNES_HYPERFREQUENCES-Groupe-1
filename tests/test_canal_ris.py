"""Tests du module canal_ris (responsable des tests : Vouffo)."""
import numpy as np
from src import config
from src.canal_ris import (positions_elements, canal_bs_ris, canal_ris_ue,
                           matrice_reflexion, canal_total)

CENTRE = np.array([35.0, 18.0, 5.0])
BS = np.array([0.0, 0.0, 10.0])
UE = np.array([40.0, 5.0, 1.5])


def test_positions_elements_forme_et_pas():
    pos = positions_elements(CENTRE, 4, 3, config.PAS_ELEMENTS)
    assert pos.shape == (12, 3)
    # tous les éléments sont dans le plan du panneau
    assert np.allclose(pos[:, 0], CENTRE[0])
    # le plus proche voisin est à une distance égale au pas
    d = np.linalg.norm(pos[0] - pos[1:], axis=1)
    assert abs(d.min() - config.PAS_ELEMENTS) < 1e-12


def test_canaux_ont_n_elements_et_sont_complexes():
    pos = positions_elements(CENTRE, 4, 4, config.PAS_ELEMENTS)
    g = canal_bs_ris(BS, pos, config.F_HZ)
    h_r = canal_ris_ue(pos, UE, config.F_HZ)
    assert g.shape == (16,) and h_r.shape == (16,)
    assert np.iscomplexobj(g) and np.iscomplexobj(h_r)


def test_matrice_reflexion_diagonale_de_module_beta():
    phases = np.array([0.0, 1.0, 2.0, 3.0])
    theta = matrice_reflexion(phases, amplitude=0.9)
    assert theta.shape == (4, 4)
    assert np.allclose(theta, np.diag(np.diag(theta)))
    assert np.allclose(np.abs(np.diag(theta)), 0.9)


def test_canal_total_phases_nulles():
    pos = positions_elements(CENTRE, 4, 4, config.PAS_ELEMENTS)
    g = canal_bs_ris(BS, pos, config.F_HZ)
    h_r = canal_ris_ue(pos, UE, config.F_HZ)
    h_d = 1e-4 * (1 + 1j)
    h = canal_total(h_d, h_r, g, np.zeros(16))
    assert abs(h - (h_d + np.sum(h_r * g))) < 1e-15
