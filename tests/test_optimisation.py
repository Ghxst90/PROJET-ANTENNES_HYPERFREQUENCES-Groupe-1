"""Tests du module optimisation (responsable des tests : Vouffo)."""
import numpy as np
import pytest
from src.optimisation import (phases_analytiques, quantifier_phases,
                              fonction_objectif, optimiser_genetique)
from src.canal_ris import canal_total


def _canaux_aleatoires(n, graine=0):
    rng = np.random.default_rng(graine)
    h_r = rng.uniform(0.5, 1.0, n) * np.exp(1j * rng.uniform(0, 2 * np.pi, n)) * 1e-3
    g = rng.uniform(0.5, 1.0, n) * np.exp(1j * rng.uniform(0, 2 * np.pi, n)) * 1e-3
    h_d = 1e-4 * np.exp(1j * 0.7)
    return h_d, h_r, g


def test_phases_analytiques_additionnent_les_amplitudes():
    h_d, h_r, g = _canaux_aleatoires(64)
    theta = phases_analytiques(h_d, h_r, g)
    h = canal_total(h_d, h_r, g, theta)
    attendu = abs(h_d) + np.sum(np.abs(h_r * g))
    assert abs(abs(h) - attendu) / attendu < 1e-9


def test_phases_dans_0_2pi():
    h_d, h_r, g = _canaux_aleatoires(64)
    theta = phases_analytiques(h_d, h_r, g)
    assert theta.min() >= 0 and theta.max() < 2 * np.pi


def test_quantification_niveaux_permis():
    phases = np.random.default_rng(1).uniform(0, 2 * np.pi, 200)
    q1 = quantifier_phases(phases, 1)
    q2 = quantifier_phases(phases, 2)
    # 1 bit : multiples de pi ; 2 bits : multiples de pi/2
    assert np.allclose(q1 / np.pi, np.round(q1 / np.pi), atol=1e-9)
    assert np.allclose(q2 / (np.pi / 2), np.round(q2 / (np.pi / 2)), atol=1e-9)


@pytest.mark.parametrize("bits, perte_attendue_db", [(1, -3.9), (2, -0.9)])
def test_perte_de_gain_due_a_la_quantification(bits, perte_attendue_db):
    # Cas sans trajet direct, beaucoup d'éléments : valeurs de la littérature
    rng = np.random.default_rng(2)
    n = 4096
    h_r = np.exp(1j * rng.uniform(0, 2 * np.pi, n))
    g = np.exp(1j * rng.uniform(0, 2 * np.pi, n))
    theta = phases_analytiques(0j, h_r, g)
    gain_ideal = abs(np.sum(h_r * g * np.exp(1j * theta))) ** 2
    thq = quantifier_phases(theta, bits)
    gain_q = abs(np.sum(h_r * g * np.exp(1j * thq))) ** 2
    perte_db = 10 * np.log10(gain_q / gain_ideal)
    assert abs(perte_db - perte_attendue_db) < 0.3


@pytest.mark.skip(reason="À activer (Vouffo) quand optimiser_genetique sera écrit")
def test_genetique_proche_de_la_solution_analytique():
    # TODO (Vouffo) : comparer le SINR obtenu par l'algorithme génétique à celui des phases
    # analytiques avec fonction_objectif, par exemple avec n = 16 éléments.
    # Critère à fixer avec Aroung (par exemple écart inférieur à 1 dB).
    h_d, h_r, g = _canaux_aleatoires(16)
    phases_opt, historique = optimiser_genetique(h_d, h_r, g, n_iterations=200, graine=0)
    ref = fonction_objectif(phases_analytiques(h_d, h_r, g), h_d, h_r, g)
    obtenu = fonction_objectif(phases_opt, h_d, h_r, g)
    assert ref - obtenu < 1.0
