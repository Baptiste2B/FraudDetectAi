from django.shortcuts import render,  redirect, get_object_or_404
from django.urls import reverse
import json
import requests
from .forms import *

import pandas as pd
import csv
import os

import plotly.express as px
import plotly.io as pio

from .function import shap_create, shap_global_summary

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponse
from django.contrib.auth import authenticate, logout, login as django_login

from .models import PredictionResult




@login_required(login_url='login')
def home(request):
    return render(request,'home.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)  # Déconnecte l'utilisateur
    return redirect('login')  # Redirige vers la page de connexion

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            return redirect('home')  # Redirige vers la page d'accueil après connexion
        else:
            return HttpResponse("Invalid credentials", status=401)
    return render(request, 'auth/login.html')
    
@login_required(login_url='login')
def predict_form(request):
    return render(request, 'tools/predict_form.html')

@login_required(login_url='login')
def upload_csv(request):
    if request.method == 'POST' and 'file' in request.FILES:
        csv_file = request.FILES['file']
        if csv_file.size > 100 * 1024 * 1024:
            return JsonResponse({'error': 'File size exceeds 100MB limit'}, status=400)
        # Enregistrement du fichier
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'csv'))
        filename = fs.save(csv_file.name, csv_file)
        file_url = fs.url(filename)

        # Lecture du CSV et conversion en JSON
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, 'csv', filename)
            df = pd.read_csv(file_path)
            data_json = df.to_json(orient='records')
        except Exception as e:
            return HttpResponseBadRequest(f"Invalid CSV file: {str(e)}")

        # Sauvegarde dans la session
        request.session['filename'] = filename
        request.session['file_url'] = file_url
        request.session['prediction'] = 'Résultat de la prédiction'

        # Envoi à l'API
        api_url = 'http://127.0.0.1:8000/api/predict_csv'
        response = requests.post(api_url, data=data_json, headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            prediction = response.json()
            if 'result' in prediction and 'predictions' in prediction['result']:
                predictions = prediction.get('result', {}).get('predictions', [])
                data = prediction.get('data', [])

                threshold_lower = 0.50
                threshold_upper = 0.65

                prediction_transformed = [
                    0 if p < threshold_lower else 1 if threshold_lower <= p < threshold_upper else 2
                    for p in predictions
                ]

                request.session['prediction'] = prediction_transformed
                request.session['data'] = prediction['data']

                # Enregistrer toutes les informations en une seule entrée
                PredictionResult.objects.create(
                    user=request.user,
                    probability=predictions,  # Liste de probabilités
                    prediction_class=prediction_transformed,  # Liste de classes de prédiction
                    shap_values=[data[i].get('shap_values', []) for i in range(len(predictions))],
                    features=[data[i].get('features', {}) for i in range(len(predictions))]
                )
                if 'single_prediction' in request.session:
                    del request.session['single_prediction']
                # return redirect('dashboard')
                return JsonResponse({'success': True, 'redirect_url': reverse('dashboard')})

            else:
                return JsonResponse({'error': 'Malformed response from the prediction API'}, status=500)

        else:
            return JsonResponse({'error': 'Failed to get a response from the prediction API'}, status=response.status_code)

    return JsonResponse({'error':"Invalid request"})


from django.http import JsonResponse
from .models import PredictionResult

@login_required(login_url='login')
def get_previous_prediction(request, prediction_id):
    prediction = PredictionResult.objects.filter(id=prediction_id, user=request.user).first()

    if prediction:
        prediction_classes = prediction.prediction_class
        count_0 = prediction_classes.count(0)
        count_1 = prediction_classes.count(1)
        count_2 = prediction_classes.count(2)
        total_predictions = len(prediction_classes)
        fraud_rate = ((count_1 + count_2) / total_predictions) * 100 if total_predictions > 0 else 0

        context = {
            'count_0': count_0,
            'count_1': count_1,
            'count_2': count_2,
            'fraud_rate': round(fraud_rate, 2),
        }

        if request.GET.get('format') == 'json':
            return JsonResponse(context)

        return render(request, 'tools/previous.html', context=context)

    if request.GET.get('format') == 'json':
        return JsonResponse({'error': 'Prediction not found'}, status=404)

    return render(request, 'tools/previous.html', context={'error': 'Prediction not found'})

@login_required(login_url='login')
def dashboard(request, prediction_id=None):
    previous_predictions = PredictionResult.objects.filter(user=request.user).order_by('-created_at')
    if prediction_id:
        prediction = get_object_or_404(PredictionResult, id=prediction_id, user=request.user)
        single_prediction = json.loads(prediction.result)
        # Retourner les données JSON pour la requête AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'single_prediction': single_prediction})
    else:
        single_prediction = request.session.get('single_prediction', {})
    # Récupérer les prédictions depuis la session
    predictions = request.session.get('prediction', [])
    single_prediction = request.session.get('single_prediction', {})
    data = pd.DataFrame(request.session.get('data', [])) 
    if not predictions and not single_prediction:
        # Cas où il n'y a aucune prédiction
        context = { 
            'count_0': 0,
            'count_1': 0,
            'count_2': 0,
            'fraud_rate': 0,
            'total_trans': 0,
            'feature_list': [],
            'graphs': {},
            'single_prediction': None,
        }
    elif single_prediction:
        # Cas de la prédiction unique
        result = single_prediction['result']
        prediction_class = result.get('prediction_class')
        probability = result.get('probability')
        shap_values = result.get('shap_values', [])
        features = result.get('features', {})
        shap_image_path_local = shap_create(shap_values, features)
        shap_image_path_global = shap_global_summary(shap_values, features)
        context = {
            'single_prediction': {
                'prediction_class': prediction_class,
                'probability': probability,
                'features': features,
            },
            'shap_image_local': shap_image_path_local,
            'shap_image_global': shap_image_path_global,
        }
        print(context)
        return render(request, 'tools/dashboard.html', context)
    else:
        # Cas des prédictions multiples via CSV
        data['fraud_bool'] = predictions
        graphs = {}
        label_mapping = {0: "No Fraud", 1: "Fraud", 2: "Potential Fraud"}
        data['fraud_bool'] = data['fraud_bool'].map(label_mapping)

        feature_list = [col for col in data.columns if col != 'fraud_bool']

        for feature in feature_list:
            fig = px.histogram(
                data, 
                x=feature, 
                color="fraud_bool", 
                nbins=50, 
                title=f"Distribution of {feature}", 
                labels={'fraud_bool': 'Type de Fraude'}
            )
            graphs[feature] = pio.to_json(fig)
        user_predictions = PredictionResult.objects.filter(user=request.user).order_by('-created_at')

        context = { 
            'previous_predictions': previous_predictions,
            'single_prediction': single_prediction,
            'user_predictions': user_predictions,
            'count_0': predictions.count(0),
            'count_1': predictions.count(1),
            'count_2': predictions.count(2),
            'fraud_rate': (predictions.count(1) + predictions.count(2)) / len(predictions) * 100 if len(predictions) > 0 else 0,
            'total_trans': len(predictions),
            'feature_list': feature_list,
            'graphs': graphs,
            'single_prediction': None,
        }

    return render(request, 'tools/dashboard.html', context)



@login_required(login_url='login')
def predict_form_a(request):
    if request.method == 'POST':
        # Retrieving form data from POST request
        data = {
            'income': float(request.POST.get('income')),
            'name_email_similarity': float(request.POST.get('name_email_similarity')),
            'prev_address_months_count': int(request.POST.get('prev_address_months_count')),
            'current_address_months_count': int(request.POST.get('current_address_months_count')),
            'customer_age': int(request.POST.get('customer_age')),
            'days_since_request': float(request.POST.get('days_since_request')),
            'intended_balcon_amount': float(request.POST.get('intended_balcon_amount')),
            'zip_count_4w': int(request.POST.get('zip_count_4w')),
            'velocity_6h': float(request.POST.get('velocity_6h')),
            'velocity_24h': float(request.POST.get('velocity_24h')),
            'velocity_4w': float(request.POST.get('velocity_4w')),
            'bank_branch_count_8w': int(request.POST.get('bank_branch_count_8w')),
            'date_of_birth_distinct_emails_4w': int(request.POST.get('date_of_birth_distinct_emails_4w')),
            'credit_risk_score': int(request.POST.get('credit_risk_score')),
            'email_is_free': int(request.POST.get('email_is_free')),
            'phone_home_valid': int(request.POST.get('phone_home_valid')),
            'phone_mobile_valid': int(request.POST.get('phone_mobile_valid')),
            'bank_months_count': int(request.POST.get('bank_months_count')),
            'has_other_cards': int(request.POST.get('has_other_cards')),
            'proposed_credit_limit': float(request.POST.get('proposed_credit_limit')),
            'foreign_request': int(request.POST.get('foreign_request')),
            'session_length_in_minutes': float(request.POST.get('session_length_in_minutes')),
            'keep_alive_session': int(request.POST.get('keep_alive_session')),
            'device_distinct_emails_8w': int(request.POST.get('device_distinct_emails_8w')),
            'device_fraud_count': int(request.POST.get('device_fraud_count')),
            'month': int(request.POST.get('month')),
            'payment_type': request.POST.get('payment_type'),  # String
            'employment_status': request.POST.get('employment_status'),  # String
            'housing_status': request.POST.get('housing_status'),  # String
            'source': request.POST.get('source'),  # String
            'device_os': request.POST.get('device_os'),  # String
        }

        # print(f"debug avant JSON {data}")

        # Convert to JSON
        json_data = json.dumps(data)
        print(f'Debug : {json_data}')

        # Envoyer les données à l'API FastAPI et obtenir la prédiction
        api_url = 'http://127.0.0.1:8000/api/predict_One'
        response = requests.post(api_url, data=json_data, headers={'Content-Type': 'application/json'})

        # Vérifier si la réponse est correcte
        if response.status_code == 200:
            prediction = response.json()

            result = prediction.get('result', {})
            PredictionResult.objects.create(
                user=request.user,
                probability=result.get('probability', 0.0),
                prediction_class=result.get('prediction_class', 0),
                shap_values=result.get('shap_values', []),
                features=result.get('features', {})
            )


            # Stocker le résultat de la prédiction unique dans la session
            request.session['single_prediction'] = prediction

            return redirect('dashboard')  # Rediriger vers le dashboard pour afficher la prédiction
        else:
            return JsonResponse({'error': 'Failed to get a response from the prediction API'}, status=response.status_code)

    return render(request, 'tools/predict_form_a.html')


@login_required(login_url='login')
def doc(request):
    return render(request,'tools/doc.html')

def read_last_csv(request):
    if 'last_uploaded_csv' in request.session:
        filename = request.session['last_uploaded_csv']
        file_path = os.path.join(settings.MEDIA_ROOT, 'csv', filename)
        
        if os.path.exists(file_path):
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                data = [row for row in reader]
            
            return JsonResponse({'data': data})
        else:
            return JsonResponse({'error': 'File not found'}, status=404)
    else:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
