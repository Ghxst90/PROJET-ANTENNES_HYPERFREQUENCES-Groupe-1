"""
config.py — Paramètres communs du projet (tous les modules importent ce fichier).

Responsable : Tsofack
Règle : toutes les valeurs numériques du scénario sont ICI, nulle part ailleurs.
Pour changer un paramètre, on le modifie dans ce fichier uniquement.

Unités : fréquences en Hz, distances en m, puissances en dBm, pertes/gains en dB,
angles en radians.
"""
import numpy as np

# --- Physique ---------------------------------------------------------------
F_HZ = 39e9                 # fréquence porteuse (39 GHz)
C = 3e8                     # vitesse de la lumière (m/s)
LAMBDA = C / F_HZ           # longueur d'onde (~7,7 mm à 39 GHz)

# --- Émetteur et récepteur --------------------------------------------------
P_TX_DBM = 30.0             # puissance d'émission de la station de base (dBm)
BANDE_HZ = 100e6            # largeur de bande (100 MHz)
FACTEUR_BRUIT_DB = 7.0      # facteur de bruit du récepteur (dB)

# --- RIS --------------------------------------------------------------------
N_X = 8                     # nombre d'éléments selon y (largeur du panneau)
N_Y = 8                     # nombre d'éléments selon z (hauteur du panneau)
N_ELEMENTS = N_X * N_Y      # nombre total d'éléments du RIS
PAS_ELEMENTS = LAMBDA / 2   # espacement entre éléments (lambda/2)
AMPLITUDE_RIS = 1.0         # module de réflexion de chaque élément (1 = sans perte)
BITS_PHASE = None           # résolution des phases : None = continue, 1 ou 2 = bits

# --- Scénario géométrique (valeurs par défaut, à discuter en groupe) --------
POS_BS = np.array([0.0, 0.0, 10.0])      # station de base (x, y, z) en m
POS_RIS = np.array([35.0, 18.0, 5.0])    # centre du RIS (panneau vertical en x = 35)
HAUTEUR_UE = 1.5                         # hauteur des utilisateurs (m)

# Obstacles : liste de rectangles (x_min, x_max, y_min, y_max) vus de dessus.
# Ici : un immeuble entre la station de base et la zone à couvrir.
OBSTACLES = [(20.0, 30.0, -10.0, 10.0)]
ATTENUATION_BLOCAGE_DB = 30.0            # atténuation ajoutée si le trajet est bloqué (hypothèse réglable)

# Zone à couvrir : grille de positions d'utilisateurs.
ZONE = {"x_min": 5.0, "x_max": 60.0, "y_min": -30.0, "y_max": 30.0, "pas": 2.0}

# --- Critère de couverture --------------------------------------------------
SEUIL_COUVERTURE_DB = 10.0  # un point est « couvert » si SINR >= ce seuil (dB)
