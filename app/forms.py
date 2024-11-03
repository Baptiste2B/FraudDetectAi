# forms.py
from django import forms
import os


class CSVUploadForm(forms.Form):
    file = forms.FileField(label='Upload your CSV file', required=True)