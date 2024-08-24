# gestion_excel/models.py  

import django
from django.db import models  
from django.contrib.auth.models import AbstractUser, Group, Permission 
from django.contrib.postgres.fields import JSONField



class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)


class DynamicData(models.Model):
    data = django.db.models.JSONField()  # Almacena los datos en formato JSON
    uploaded_at = models.DateTimeField(auto_now_add=True)
