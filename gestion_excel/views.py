# myapp/views.py
import pandas as pd
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from .forms import UploadFileForm
from .models import DynamicData  # Crea este modelo según la estructura de tus datos
from django.http import HttpResponse
from .models import DynamicData
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

User = get_user_model()

def home(request):
    return render(request, 'home.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la página de inicio u otra página después del login
        else:
            # Manejo de errores (opcional)
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def handle_uploaded_file(file):
    df = pd.read_excel(file)
    data_list = df.to_dict(orient='records')  # Convierte el DataFrame en una lista de diccionarios
    for data in data_list:
        DynamicData.objects.create(data=data)

@login_required
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']  # Asegúrate de que el campo del formulario se llama 'file'
        df = pd.read_excel(file)

        for _, row in df.iterrows():
            data = row.to_dict()  # Convierte la fila en un diccionario
            DynamicData.objects.create(data=data)  # Almacena en la base de datos
        
        return render(request, 'upload.html', {'message': 'File uploaded successfully'})
    return render(request, 'upload.html')
@login_required
def data_table(request):
    data_entries = DynamicData.objects.all()
    
    # Extrae las claves únicas para los encabezados de columna
    headers = set()
    for entry in data_entries:
        headers.update(entry.data.keys())
    headers = sorted(headers)
    
    # Ordena los datos para tener una estructura uniforme
    rows = []
    for entry in data_entries:
        row = [entry.data.get(header, '') for header in headers]
        rows.append(row)
    
    return render(request, 'data_table.html', {'headers': headers, 'rows': rows})

@login_required
def generate_report(request):
    data = DynamicData.objects.all().values()
    df = pd.DataFrame(list(data))
    report = df.describe()  # Ejemplo de análisis
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    df.to_csv(path_or_buf=response, index=False)
    return response