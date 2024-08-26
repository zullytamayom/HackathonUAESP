# myapp/views.py
import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
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
from .forms import DynamicDataForm
from django.core.paginator import Paginator

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

def sanitize_json(value):
    """Sanitiza los valores para que sean válidos JSON."""
    if isinstance(value, float) and (value != value):  # Check for NaN
        return None
    if isinstance(value, str) and value.strip().lower() in ["nan", ""]:
        return None
    return value
@login_required
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return HttpResponse("No file uploaded", status=400)
        
        try:
            # Leer el archivo Excel
            df = pd.read_excel(file)
            
            # Convertir el DataFrame a un diccionario
            data_dict = df.to_dict(orient='records')
            
            # Sanitizar datos
            sanitized_data = []
            for record in data_dict:
                sanitized_record = {k: sanitize_json(v) for k, v in record.items()}
                sanitized_data.append(sanitized_record)
            
            # Guardar datos en la base de datos
            for record in sanitized_data:
                DynamicData.objects.create(data=record)
                
            return HttpResponse("File uploaded and data saved successfully.")
        
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}", status=500)
    
    return render(request, 'upload.html')
def get_table_data():
    rows = DynamicData.objects.all()
    headers = ['ID']
    
    if rows.exists():
        sample_data = rows.first().data
        if isinstance(sample_data, dict):
            headers.extend(sample_data.keys())
    
    row_data = []
    for row in rows:
        data_row = [row.id]
        data_row.extend(row.data.get(key, '') for key in headers[1:])
        row_data.append(data_row)
    
    return headers, row_data
@login_required
def data_table(request):
    rows = DynamicData.objects.all()
    headers = ['ID']  # Incluye el campo 'ID' como columna
    
    # Extraer las claves del JSON para las columnas
    if rows.exists():
        sample_data = rows.first().data
        if isinstance(sample_data, dict):
            headers.extend(sample_data.keys())
    
    # Convertir los objetos de la base de datos en una lista de listas para la tabla
    row_data = []
    for row in rows:
        data_row = [row.id]  # Empieza con el campo 'ID'
        data_row.extend(row.data.get(key, '') for key in headers[1:])  # Agrega los valores del JSON
        row_data.append(data_row)
    headers, rows = get_table_data()
    records_per_page = request.GET.get('records_per_page', 10)  # 10 es el valor predeterminado
    records_per_page = int(records_per_page)  # Convertir a entero

    # Crear un paginador con el número de registros por página seleccionado
    paginator = Paginator(rows, records_per_page)

    # Obtener el número de página desde la URL
    page_number = request.GET.get('page')
    
    # Obtener la página actual
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'data_table.html', {
        'rows': page_obj, 
        'headers': headers, 
        'page_obj': page_obj, 
        'records_per_page': records_per_page
    })

def edit_record(request, id):
    record = get_object_or_404(DynamicData, id=id)
    
    if request.method == 'POST':
        form = DynamicDataForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('data_table')
    else:
        form = DynamicDataForm(instance=record)
    
    return render(request, 'edit_record.html', {'form': form, 'record': record})

def delete_record(request, id):
    record = get_object_or_404(DynamicData, id=id)
    if request.method == 'POST':
        record.delete()
        return redirect('data_table')
@login_required
def generate_report(request):
    data = DynamicData.objects.all().values()
    df = pd.DataFrame(list(data))
    report = df.describe()  # Ejemplo de análisis
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    df.to_csv(path_or_buf=response, index=False)
    return response