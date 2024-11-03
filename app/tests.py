from django.test import TestCase
from django.contrib.auth.models import User
from .models import PredictionResult
from django.urls import reverse
from django.http import JsonResponse

class PredictionResultModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_create_prediction_result(self):
        result = PredictionResult.objects.create(
            user=self.user,
            probability=[0.85],
            prediction_class=[1],
            shap_values={"feature1": 0.1, "feature2": -0.2},
            features={"feature1": 0.5, "feature2": 0.6},
        )
        self.assertEqual(result.user.username, "testuser")
        self.assertIsInstance(result.probability, list)
        self.assertEqual(result.prediction_class, [1])

class PredictionResultViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.prediction = PredictionResult.objects.create(
            user=self.user,
            probability=[0.85],
            prediction_class=[1],
            shap_values={"feature1": 0.1, "feature2": -0.2},
            features={"feature1": 0.5, "feature2": 0.6},
        )

    def test_get_previous_prediction_view(self):
        response = self.client.get(
            reverse('get_previous_prediction', args=[self.prediction.id]) + '?format=json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("count_0", response.json())