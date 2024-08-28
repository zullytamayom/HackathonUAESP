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
from .forms import DynamicDataForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import datetime
from django.views.decorators.http import require_POST



User = get_user_model()

def home(request):
    return render(request, 'home.html')
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')  # Redirige a /home/ si el usuario ya está autenticado
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la página de inicio u otra página después del login
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def handle_uploaded_file(file):
    df = pd.read_excel(file)
    data_list = df.to_dict(orient='records')  # Convierte el DataFrame en una lista de diccionarios
    for data in data_list:
        DynamicData.objects.create(data=data)

def sanitize_json(value):
    if isinstance(value, datetime):
        return value.isoformat()  # Convertir datetime a formato ISO
    if isinstance(value, list):
        return [sanitize_json(v) for v in value]
    if isinstance(value, dict):
        return {k: sanitize_json(v) for k, v in value.items()}
    return value

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
    # Obtener todos los registros
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
    
    # Configuración de la paginación
    records_per_page = request.GET.get('records_per_page', 10)  # Valor predeterminado: 10
    records_per_page = int(records_per_page)  # Convertir a entero

    # Crear un paginador con el número de registros por página seleccionado
    paginator = Paginator(row_data, records_per_page)

    # Obtener el número de página desde la URL
    page_number = request.GET.get('page')
    
    # Obtener la página actual
    page_obj = paginator.get_page(page_number)
    
   
    
    return render(request, 'data_table.html',{
        'rows': page_obj, 
        'headers': headers, 
        'page_obj': page_obj, 
        'records_per_page': records_per_page,
        'total_records': rows.count(),  # Total de registros
        'filtered_records': page_obj.paginator.count,  # Registros en la página actual (filtrados),
        'user': request.user,
        
    })

# def delete_record(request, id):
#     record = get_object_or_404(DynamicData, id=id)
#     if request.method == 'POST':
#         record.delete()
#         return redirect('data_table')
@csrf_exempt
def update_record(request, id):
    if request.method == 'POST':
        record = get_object_or_404(DynamicData, id=id)
        form = DynamicDataForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})


@login_required
@require_POST
def delete_record(request, id):
    record = get_object_or_404(DynamicData, id=id)
    record.delete()
    return JsonResponse({'status': 'success'})

def filter_records(request):
    filters = {key: value for key, value in request.GET.items() if key.startswith('filter-') and value}
    queryset = DynamicData.objects.all()  

    field_names = [field.name for field in DynamicData._meta.fields]  # Obtén todos los nombres de campos del modelo

    for key, value in filters.items():
        column_index = int(key.split('-')[1])
        field_name = field_names[column_index]

        if field_name:
            queryset = queryset.filter(**{f"{field_name}__icontains": value})

    data = list(queryset.values(*field_names))
    return JsonResponse({'data': data, 'fields': field_names}, safe=False)

