from sklearn.metrics import roc_auc_score
import pandas as pd
import pickle
from sklearn.preprocessing import OneHotEncoder
import json
import mlflow
import sklearn
import numpy as np
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import shap

def align_dataframe_with_model(df, model):
    # Extraire les noms de colonnes dans l'ordre du modèle

    model_columns = model.feature_names
    if model_columns is None:
        raise ValueError("Les noms des colonnes ne sont pas disponibles dans le modèle.")
    # Ajouter les colonnes manquantes avec des valeurs par défaut (0 ou NaN)
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0  # ou np.nan si vous préférez

    # Réorganiser les colonnes selon l'ordre du modèle
    df_aligned = df[model_columns]

    return df_aligned


def prepare_data(data):
    # Vérifier que `data` est bien un DataFrame
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    # Définir les colonnes catégorielles
    categorical_columns = ['payment_type', 'employment_status', 'housing_status', 'source', 'device_os']

    # Vérifier que toutes les colonnes catégorielles sont présentes dans `data`
    missing_cols = [col for col in categorical_columns if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Les colonnes suivantes sont manquantes dans le DataFrame: {missing_cols}")

    # Effectuer l'encodage OneHot
    ohe = OneHotEncoder(sparse_output=False)
    encoded_features = ohe.fit_transform(data[categorical_columns])
    encoded_df = pd.DataFrame(encoded_features, columns=ohe.get_feature_names_out(categorical_columns))

    # Supprimer les colonnes catégorielles d'origine du DataFrame
    data = data.drop(columns=categorical_columns)

    # Combiner les colonnes encodées avec les autres données non catégorielles
    combined_df = pd.concat([data.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
    columns_to_drop = ['x1', 'x2', 'fraud_bool']
    combined_df = combined_df.drop(columns=[col for col in columns_to_drop if col in combined_df.columns])

    return combined_df

def prepare_data_a(data):
    # Convertir les données en DataFrame
    if isinstance(data, dict):
        data = pd.DataFrame([data])  # Créer un DataFrame à une seule ligne à partir d'un dict

    # Définir les colonnes catégorielles
    categorical_columns = ['payment_type', 'employment_status', 'housing_status', 'source', 'device_os']

    # Vérifier que toutes les colonnes catégorielles sont présentes dans `data`
    missing_cols = [col for col in categorical_columns if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Les colonnes suivantes sont manquantes dans le DataFrame: {missing_cols}")

    # Effectuer l'encodage OneHot
    ohe = OneHotEncoder(sparse_output=False)
    encoded_features = ohe.fit_transform(data[categorical_columns])
    encoded_df = pd.DataFrame(encoded_features, columns=ohe.get_feature_names_out(categorical_columns))

    # Supprimer les colonnes catégorielles d'origine du DataFrame
    data = data.drop(columns=categorical_columns)

    # Combiner les colonnes encodées avec les autres données non catégorielles
    combined_df = pd.concat([data.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)

    return combined_df

def verifData(df):
    '''Vérifie si le DataFrame contient plus de 300 lignes'''
    return len(df) > 300


def predict_csv(df):
    try:
        model = xgb.Booster()
        model.load_model("project/api/model.xgb")
        print("Modèle chargé avec succès.")
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {e}")
        return {"error": str(e)}
    # Aligner les colonnes
    try:
        X_test = align_dataframe_with_model(df, model)
        print(f"X_test aligné avec succès. Forme: {X_test.shape}")
    except Exception as e:
        print(f"Erreur lors de l'alignement des colonnes: {e}")
        return {"error": str(e)}
    # Créer un DMatrix
    try:
        d_test = xgb.DMatrix(X_test)
        print("DMatrix créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création du DMatrix: {e}")
        return {"error": str(e)} 
    # Faire des prédictions
    try:
        y_prob = model.predict(d_test)
        print("Prédictions réalisées avec succès.")
    except Exception as e:
        print(f"Erreur lors de la prédiction: {e}")
        return {"error": str(e)}
    print(y_prob.tolist())
    results_df = df.copy()  # Copier le DataFrame original
    results_df['Probability'] = y_prob  # Ajouter les probabilités
    print(results_df.columns)
    return {
        "results": results_df.to_dict(orient="records"),
        "predictions": y_prob.tolist(),  # Probabilités continues
    }


import numpy as np
from fastapi.encoders import jsonable_encoder

def predict_one(df):
    try:
        model = xgb.Booster()
        model.load_model("project/api/model.xgb")
        print("Modèle chargé avec succès.")
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {e}")
        return {"error": str(e)}

    try:
        # Aligner le DataFrame avec les colonnes du modèle
        df_aligned = align_dataframe_with_model(df, model)
        print(f"Colonnes alignées avec succès. Forme: {df_aligned.shape}")

        # Créer le DMatrix pour XGBoost
        dmatrix = xgb.DMatrix(df_aligned)
        y_prob = model.predict(dmatrix)[0]

        # Calcul des valeurs SHAP
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(dmatrix)

        threshold_lower = 0.50
        threshold_upper = 0.65

        if y_prob < threshold_lower:
            prediction_class = 0  # Non-fraude
        elif threshold_lower <= y_prob < threshold_upper:
            prediction_class = 1  # Fraude potentielle
        else:
            prediction_class = 2  # Fraude certaine

        # Conversion des types numpy en types natifs Python
        y_prob = float(y_prob)
        shap_values = shap_values.tolist()
        features = {key: (float(value) if isinstance(value, np.generic) else value) for key, value in df_aligned.iloc[0].items()}

        return {
            "probability": y_prob,
            "prediction_class": prediction_class,
            "shap_values": shap_values,
            "features": features
        }
    except Exception as e:
        return {"error": str(e)}