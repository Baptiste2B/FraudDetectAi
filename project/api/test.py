import unittest
import pandas as pd
import numpy as np
from project.api.views import prepare_data, align_dataframe_with_model, predict_one

class TestModelFunctions(unittest.TestCase):
    
    def setUp(self):
        # Ceci est exécuté avant chaque test
        self.sample_data = {
            'income': [50000],
            'name_email_similarity': [0.8],
            'prev_address_months_count': [12],
            'current_address_months_count': [6],
            'customer_age': [45],
            'days_since_request': [2.5],
            'intended_balcon_amount': [1000.5],
            'zip_count_4w': [10],
            'velocity_6h': [1.2],
            'velocity_24h': [3.5],
            'velocity_4w': [10],
            'bank_branch_count_8w': [2],
            'date_of_birth_distinct_emails_4w': [1],
            'credit_risk_score': [600],
            'email_is_free': [1],
            'phone_home_valid': [1],
            'phone_mobile_valid': [1],
            'bank_months_count': [24],
            'has_other_cards': [0],
            'proposed_credit_limit': [1500],
            'foreign_request': [0],
            'session_length_in_minutes': [35],
            'keep_alive_session': [1],
            'device_distinct_emails_8w': [1],
            'device_fraud_count': [0],
            'month': [7],
            'payment_type': ['AA'],
            'employment_status': ['CA'],
            'housing_status': ['BC'],
            'source': ['INTERNET'],
            'device_os': ['linux']
        }
        self.sample_df = pd.DataFrame(self.sample_data)

    def test_prepare_data(self):
        # Test si la fonction prepare_data fonctionne correctement
        df = prepare_data(self.sample_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue('payment_type_AA' in df.columns)

    def test_align_dataframe_with_model(self):
        # Simuler un modèle factice avec des colonnes spécifiques
        class FakeModel:
            feature_names = ['income', 'name_email_similarity', 'prev_address_months_count', 'current_address_months_count', 'customer_age', 'days_since_request']

        df = pd.DataFrame({
            'income': [50000],
            'name_email_similarity': [0.8],
            'prev_address_months_count': [12]
        })

        aligned_df = align_dataframe_with_model(df, FakeModel())
        self.assertEqual(aligned_df.shape[1], 6)
        self.assertIn('current_address_months_count', aligned_df.columns)

    def test_predict_one(self):
        # Test la prédiction unique
        prediction_result = predict_one(self.sample_df)
        self.assertIn('probability', prediction_result)
        self.assertIn('prediction_class', prediction_result)
        self.assertIsInstance(prediction_result['shap_values'], list)
        self.assertIsInstance(prediction_result['features'], dict)

if __name__ == '__main__':
    unittest.main()