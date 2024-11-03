from django.contrib import admin
from django.urls import path,include
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static


# myapp/urls.py
from django.urls import path
from .views import predict_form, login, home, predict_form_a, dashboard, upload_csv,read_last_csv, doc, logout_view

urlpatterns = [
    path('', login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('home/', home, name='home'),
    path('dashboard/predictCSV/', predict_form, name='predict-form'),
    path('dashboard/predictAlone/', predict_form_a, name='predict-form-a'),
    path('dashboard/', dashboard, name='dashboard'),
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('read_last_csv/', read_last_csv, name='read_last_csv'),
    path('dashboard/doc/', doc, name="doc" ),
    path('get_previous_prediction/<int:prediction_id>/', views.get_previous_prediction, name='get_previous_prediction'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
