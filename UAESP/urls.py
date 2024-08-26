from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView 
from gestion_excel import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('admin/', admin.site.urls),
    path('', include('gestion_excel.urls')),
    path('upload/', include('gestion_excel.urls')),  # Incluye las rutas de la aplicación 'gestion_excel'
    path('data/', include('gestion_excel.urls')),
    path('edit_<int:id>/', include('gestion_excel.urls')),
    path('delete_<int:id>/', include('gestion_excel.urls')),
    path('report/', include('gestion_excel.urls')),  # Similar para otras rutas
    path('', include('gestion_excel.urls')),

    
]