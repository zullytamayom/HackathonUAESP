# gestion_excel/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Personaliza la configuración del admin si es necesario

admin.site.register(CustomUser, CustomUserAdmin)


