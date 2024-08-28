# gestion_excel/urls.py  

from django.urls import path  
from django.contrib.auth.views import LogoutView
from . import views





urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('upload/', views.upload_file, name='upload_file'),
    path('data/', views.data_table, name='data_table'),
    path('update/<int:id>/', views.update_record, name='update_record'),
    path('delete/<int:id>/', views.delete_record, name='delete_record'),
    # path('report/', views.generate_report, name='generate_report'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

]