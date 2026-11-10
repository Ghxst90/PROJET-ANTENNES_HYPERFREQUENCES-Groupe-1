"""
optimisation.py — Choix des phases du RIS qui maximisent la qualité de réception.

Responsable : Aroung (Module D)   Soutien : Tsofack
Dépend de : metriques (SINR), canal_ris (canal total)
Utilisé par : simulation.py, sensibilite.py, tests/test_optimisation.py

Unités : phases en radians.
"""
import numpy as np
from src import config
from src import metriques
from src import canal_ris


def phases_analytiques(h_d, h_r, g):
    """Solution optimale pour UN utilisateur : tous les trajets s'additionnent en phase.

    Entrées : h_d (complexe), h_r et g (vecteurs complexes de taille N)
    Sortie  : vecteur de N phases en rad, dans [0, 2*pi[
        theta[n] = arg(h_d) - arg(h_r[n] * g[n])
    Avec ces phases, |h| = |h_d| + somme_n |h_r[n] * g[n]| (amplitudes qui s'ajoutent).
    Sert de RÉFÉRENCE pour valider les algorithmes heuristiques.
    """
    return np.mod(np.angle(h_d) - np.angle(np.asarray(h_r) * np.asarray(g)), 2 * np.pi)


def quantifier_phases(phases, bits):
    """Arrondit les phases aux 2**bits valeurs permises par le matériel.

    Entrées : phases (rad), bits (1, 2, ...)
    Sortie  : phases arrondies au multiple de 2*pi / 2**bits le plus proche
    Ordre de grandeur attendu : environ -4 dB de gain avec 1 bit, -1 dB avec 2 bits.
    """
    pas = 2 * np.pi / 2 ** bits
    return np.mod(np.round(np.asarray(phases) / pas) * pas, 2 * np.pi)


def fonction_objectif(phases, h_d, h_r, g, interferences_dbm=None):
    """Critère à MAXIMISER : SINR (dB) pour un utilisateur, avec ces phases.

    Entrées : phases (N rad), h_d, h_r, g (voir ci-dessus), interferences_dbm (ou None)
    Sortie  : SINR en dB, calculé avec canal_ris.canal_total puis metriques.puissance_recue_dbm,
              metriques.bruit_dbm et metriques.sinr_db (paramètres pris dans config.py)
    """
    h = canal_ris.canal_total(h_d, h_r, g, phases)
    p_rx = metriques.puissance_recue_dbm(config.P_TX_DBM, h)
    return metriques.sinr_db(p_rx, metriques.bruit_dbm(), interferences_dbm)


def _evaluer(population, h_d, h_r, g):
    """SINR (dB) de chaque individu d'une population de phases, calculé d'un seul coup.

    Entrées : population (tableau (P, N) de phases en rad), h_d, h_r, g
    Sortie  : tableau de P valeurs de SINR en dB
    (Même calcul que fonction_objectif, mais vectorisé pour aller vite.)
    """
    hg = np.asarray(h_r) * np.asarray(g)                      # cascade de chaque élément
    h = h_d + (config.AMPLITUDE_RIS * np.exp(1j * population) * hg).sum(axis=1)
    p_rx = metriques.puissance_recue_dbm(config.P_TX_DBM, h)
    return metriques.sinr_db(p_rx, metriques.bruit_dbm())


def _contraindre(phases, bits):
    """Ramène les phases dans [0, 2*pi[ et les quantifie si le matériel est à `bits` bits."""
    phases = np.mod(phases, 2 * np.pi)
    return quantifier_phases(phases, bits) if bits else phases


def optimiser_genetique(h_d, h_r, g, taille_population=50, n_iterations=100,
                        bits=config.BITS_PHASE, graine=None):
    """Algorithme génétique pour trouver de bonnes phases.

    Entrées : h_d, h_r, g ; taille_population ; n_iterations ;
              bits (None = phases continues) ; graine (pour reproduire les résultats)
    Sortie  : (meilleures_phases, historique)
              historique = liste du meilleur SINR (dB) à chaque itération
    Étapes classiques : population aléatoire, évaluation, sélection, croisement,
    mutation, répétition.
    """
    rng = np.random.default_rng(graine)
    n = len(g)
    p = taille_population
    n_elite = max(1, p // 10)                  # les meilleurs passent tels quels (élitisme)
    taux_croisement = 0.8
    taux_mutation = max(0.05, 1.0 / n)         # probabilité de muter pour chaque phase

    # 1. Population de départ : phases tirées au hasard
    pop = _contraindre(rng.uniform(0, 2 * np.pi, (p, n)), bits)
    score = _evaluer(pop, h_d, h_r, g)
    historique = []

    for it in range(n_iterations):
        # 2. Sélection par tournoi : parmi 3 individus au hasard, on garde le meilleur
        candidats = rng.integers(0, p, (p, 3))
        gagnants = candidats[np.arange(p), np.argmax(score[candidats], axis=1)]
        parents = pop[gagnants]

        # 3. Croisement uniforme : chaque phase vient d'un parent ou de son partenaire
        partenaires = parents[rng.permutation(p)]
        echange = (rng.random((p, n)) < 0.5) & (rng.random(p) < taux_croisement)[:, None]
        enfants = np.where(echange, partenaires, parents)

        # 4. Mutation
        mute = rng.random((p, n)) < taux_mutation
        if bits:
            # phases discrètes : on retire un niveau au hasard
            enfants = np.where(mute, rng.uniform(0, 2 * np.pi, (p, n)), enfants)
        else:
            # phases continues : petite perturbation qui diminue au fil des itérations
            ecart = 0.8 * (1 - it / n_iterations) + 0.02          # en radians
            enfants = enfants + mute * rng.normal(0, ecart, (p, n))
        enfants = _contraindre(enfants, bits)

        # 5. Élitisme : on réinjecte les meilleurs de la génération précédente
        meilleurs = pop[np.argsort(score)[-n_elite:]]
        enfants[:n_elite] = meilleurs

        pop = enfants
        score = _evaluer(pop, h_d, h_r, g)
        historique.append(float(score.max()))

    return pop[np.argmax(score)], historique


def optimiser_pso(h_d, h_r, g, n_particules=30, n_iterations=100,
                  bits=config.BITS_PHASE, graine=None):
    """Essaim de particules (optionnel : à faire si le temps le permet).

    Mêmes entrées et sorties que optimiser_genetique.
    """
    rng = np.random.default_rng(graine)
    n = len(g)
    p = n_particules
    c1, c2 = 1.5, 1.5                          # poids de la mémoire de la particule et du groupe

    pos = rng.uniform(0, 2 * np.pi, (p, n))    # une position = un jeu de phases
    vit = rng.uniform(-0.5, 0.5, (p, n))
    score = _evaluer(_contraindre(pos, bits), h_d, h_r, g)
    pbest, pbest_score = pos.copy(), score.copy()          # meilleur passé de chaque particule
    ibest = np.argmax(score)
    gbest, gbest_score = pos[ibest].copy(), score[ibest]   # meilleur du groupe
    historique = []

    for it in range(n_iterations):
        w = 0.9 - 0.5 * it / n_iterations      # inertie décroissante : explorer puis affiner
        r1, r2 = rng.random((p, n)), rng.random((p, n))
        # les phases sont circulaires : on mesure les écarts sur le cercle, entre -pi et pi
        vers_pbest = np.angle(np.exp(1j * (pbest - pos)))
        vers_gbest = np.angle(np.exp(1j * (gbest - pos)))
        vit = np.clip(w * vit + c1 * r1 * vers_pbest + c2 * r2 * vers_gbest, -np.pi, np.pi)
        pos = np.mod(pos + vit, 2 * np.pi)

        score = _evaluer(_contraindre(pos, bits), h_d, h_r, g)
        mieux = score > pbest_score
        pbest[mieux], pbest_score[mieux] = pos[mieux], score[mieux]
        ibest = np.argmax(pbest_score)
        if pbest_score[ibest] > gbest_score:
            gbest, gbest_score = pbest[ibest].copy(), pbest_score[ibest]
        historique.append(float(gbest_score))

    return _contraindre(gbest, bits), historique