# Projet RIS — Couverture à 39 GHz assistée par surface intelligente

Projet d'Antennes et Hyperfréquences, Thème 1.
Modélisation et optimisation de la couverture 5G-Advanced / 6G en bande millimétrique (39 GHz)
par une Surface Intelligente Reconfigurable (RIS).

## Le projet en quelques lignes

Les ondes à 39 GHz s'atténuent fortement (environ 64 dB à 1 m) et sont bloquées par les
obstacles, ce qui crée des zones d'ombre. Un **RIS** est un panneau d'éléments qui réfléchissent
l'onde en décalant sa phase. En choisissant bien ces phases, on redirige le signal vers
l'utilisateur caché. Le code de ce dépôt :

1. modélise le canal direct et le canal réfléchi par le RIS ;
2. optimise les phases du RIS ;
3. calcule des cartes de SINR avec et sans RIS, et des indicateurs de performance ;
4. étudie l'effet des paramètres (nombre d'éléments, résolution des phases, position du RIS).

## Équipe et responsabilités

| Membre | Rôle | Fichiers dont il est responsable |
|---|---|---|
| Aissatou | Responsable de groupe | `src/metriques.py`, `docs/` |
| Aroung | Adjoint | `src/canal_direct.py`, `src/optimisation.py`, `README.md` |
| Tsala | Membre | `src/canal_ris.py`, `src/visualisation.py`, `figures/` |
| Tsofack | Membre | `src/config.py`, `src/simulation.py`, `resultats/`, `requirements.txt`, `.gitignore` |
| Vouffo | Membre | `src/sensibilite.py`, `tests/` |

## Organisation du dépôt

```
projet-ris/
├── README.md
├── requirements.txt
├── conftest.py            (permet à pytest de trouver le dossier src)
├── src/
│   ├── config.py          Paramètres communs
│   ├── canal_direct.py    Canal direct BS -> UE
│   ├── canal_ris.py       RIS et canal BS -> RIS -> UE
│   ├── optimisation.py    Choix des phases du RIS
│   ├── metriques.py       SINR, couverture, débit
│   ├── visualisation.py   Cartes et courbes
│   ├── simulation.py      Assemblage (fichier principal)
│   └── sensibilite.py     Études de sensibilité
├── tests/                 Tests de validation
├── resultats/             Données produites par les simulations
├── figures/               Images pour le rapport
└── docs/                  Plan de travail, slides, rapport
```

Chaque fichier de `src/` contient des fonctions déjà **nommées et décrites** (entrées, sorties,
formules). Chacun remplace `raise NotImplementedError(...)` par son code, **sans changer le
nom ni les entrées/sorties** des fonctions, car les autres membres s'en servent.

## Installation

```bash
git clone <adresse du dépôt>
cd projet-ris
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer la simulation et les tests

```bash
python -m src.simulation         # lance le scénario par défaut (quand simulation.py est écrit)
pytest                           # lance tous les tests
```

**Tant que les fonctions ne sont pas écrites, les tests échouent : c'est normal.**
Un test qui passe confirme qu'une fonction donne le résultat attendu ; un test qui échoue
après qu'on l'a écrite signale une erreur à corriger.

## Conventions communes (à respecter partout)

| Grandeur | Convention |
|---|---|
| Fréquence | en Hz (`39e9` pour 39 GHz) |
| Distances, positions | en mètres ; une position est un tableau numpy `(x, y, z)` |
| Longueur d'onde | `lambda = c / f`, environ 7,7 mm à 39 GHz ; espacement des éléments du RIS = lambda/2 |
| Puissances | en dBm ; pertes et gains en dB |
| Angles, phases | en radians |
| Coefficients de canal | nombres complexes numpy |
| Noms | français sans accent, avec tirets bas (`perte_espace_libre`) |
| Documentation | chaque fonction a une docstring : rôle, entrées, sorties, unités |

### Convention pour le canal réfléchi (décision à garder dans le rapport)

- `g` : canal physique BS vers éléments du RIS (vecteur complexe de taille N).
- `h_r` : canal physique éléments du RIS vers UE (vecteur complexe de taille N), **sans conjugaison**.
- Signal total : `h = h_d + somme_n( h_r[n] * beta * exp(j*theta[n]) * g[n] )`,
  soit `h_r^T . Theta . g`. La notation `h_r^H` du plan de travail vient d'une autre
  définition de `h_r` et doit être harmonisée dans le rapport.
- Phases optimales pour un utilisateur : `theta[n] = arg(h_d) - arg(h_r[n] * g[n])`.
- Les éléments du RIS sont supposés isotropes (hypothèse simplificatrice).

## Qui dépend de qui

| Fichier | Utilise |
|---|---|
| `simulation.py` | `config`, `canal_direct`, `canal_ris`, `optimisation`, `metriques` |
| `optimisation.py` | `canal_ris`, `metriques` |
| `canal_ris.py` | `canal_direct` (perte en espace libre) |
| `metriques.py` | `config` |
| `visualisation.py` | résultats de `simulation.py` |
| `sensibilite.py` | `simulation`, `visualisation` |

## Travailler avec Git

1. **Une branche par personne et par module**, par exemple `aroung-canal-direct`, `tsala-canal-ris`.
   Personne ne travaille directement sur `main`.
2. Avant de commencer : `git pull` pour récupérer le travail des autres.
3. Commits fréquents avec un message court : `ajout de perte_espace_libre`.
4. Fusion vers `main` quand les fonctions du fichier marchent, ont une docstring et que
   les tests concernés passent. Tsofack fait les fusions après relecture par un autre membre.
5. Ne pas versionner de gros fichiers de résultats.

## Ordre de développement conseillé

| Semaine | À faire en priorité |
|---|---|
| 4 | Tsofack : `config.py` et squelette de `simulation.py`. Aroung et Tsala : premières versions de `canal_direct` et `canal_ris`. Aissatou : `metriques.py`. Vouffo : premiers tests. |
| 5 | Aissatou : `metriques.py` complet. Aroung : phases analytiques. Tsofack : première simulation avec un seul utilisateur. |
| 6 | Aroung : algorithme génétique. Tsala : visualisation. Vouffo : tests d'optimisation. Tsofack : intégration et scénarios. |
| 6 - 7 | Vouffo : `sensibilite.py` et courbes. Tsala et Aissatou : figures et comparaison pour le rapport. |
