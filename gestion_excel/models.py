# gestion_excel/models.py  

import django
from django.db import models  
from django.contrib.auth.models import AbstractUser, Group, Permission 
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
import json



class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)


class DynamicData(models.Model):
    data = models.JSONField()  # Django 3.1+ (previously used PostgreSQL JSONField)
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def clean(self):
        super().clean()
        # Validar que los datos sean JSON válidos
        try:
            json.dumps(self.data)
        except (TypeError, OverflowError) as e:
            raise ValidationError(f"Invalid JSON data: {e}")
        