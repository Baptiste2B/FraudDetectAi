import os
import shap
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from django.conf import settings
import uuid
import time

matplotlib.use('Agg')  # Utilise le backend Agg pour les graphismes hors écran


def shap_create(shap_values, features):
    # Assurez-vous que les shap_values sont sous forme de tableau numpy
    shap_values = np.array(shap_values)

    # Si features est un dictionnaire, extraire les noms des features
    feature_names = list(features.keys())
    feature_values = np.array(list(features.values()))

    # Prenez la première instance pour l'exemple
    shap_value_instance = shap_values[0]
    feature_instance = feature_values

    # Si base_values est None, utiliser une valeur par défaut de 0
    base_values = shap_value_instance.base_values if hasattr(shap_value_instance, 'base_values') else 0

    # Créer un graphique Waterfall SHAP avec une figure plus grande
    plt.figure(figsize=(12, 10))  # Augmentez la taille de la figure (largeur, hauteur)

    # Limiter à un plus grand nombre de features (par exemple 20)
    shap_plot = shap.plots.waterfall(
        shap.Explanation(values=shap_value_instance,
                         base_values=base_values,
                         data=feature_instance,
                         feature_names=feature_names),
        max_display=20  # Affichez jusqu'à 20 features
    )

    #améliorez la visibilité des labels
    plt.gca().tick_params(axis='y', labelsize=12, pad=10)  # Augmentez la taille et le padding des labels

    # Générer un nom de fichier unique pour éviter les conflits
    filename = f"shap_plot_{uuid.uuid4().hex}.png"

    # Chemin complet où l'image sera enregistrée
    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    # Sauvegarder l'image dans le chemin spécifié
    plt.savefig(file_path, format='png', bbox_inches='tight')
    plt.close()  # Fermer la figure pour libérer de la mémoire

    while True:
        if os.path.exists(file_path):
            break
        time.sleep(0.1)  # Pause de 100 ms


    # Retourner le chemin relatif à utiliser dans les templates Django
    return os.path.join(settings.MEDIA_URL, filename)


def shap_global_summary(shap_values, features):

    # Vérifier si features est un dict ou une liste de dicts
    if isinstance(features, dict):
        features_df = pd.DataFrame([features])  # Cas d'une seule prédiction
    else:
        features_df = pd.DataFrame(features)  # Cas de plusieurs prédictions

    # Vérifier que shap_values est bien un numpy array
    shap_values = np.array(shap_values)

    # Générer le graphique SHAP summary
    plt.figure()
    shap.summary_plot(shap_values, features_df, plot_type="bar")

    # Générer un nom de fichier unique
    filename = f"shap_global_summary_{uuid.uuid4().hex}.png"

    # Chemin complet où l'image sera enregistrée
    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    # Sauvegarder l'image dans le chemin spécifié
    plt.savefig(file_path, format='png')
    plt.close()  # Fermer la figure pour libérer de la mémoire

    return os.path.join(settings.MEDIA_URL, filename)