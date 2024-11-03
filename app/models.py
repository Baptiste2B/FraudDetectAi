from django.db import models
from django.contrib.auth.models import User


class PredictionResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    probability = models.JSONField()  # Utiliser JSONField pour stocker une liste de probabilités
    prediction_class = models.JSONField()  # Utiliser JSONField pour stocker une liste de classes de prédiction
    shap_values = models.JSONField()  # Enregistre les valeurs SHAP sous forme de JSON
    features = models.JSONField()  # Enregistre les features sous forme de JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.id} for user {self.user.username} with probability {self.probability}"