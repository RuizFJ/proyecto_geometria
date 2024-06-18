from django.db import models

# Create your models here.

class Formula(models.Model):
    expression = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    type = models.CharField(max_length=20)  # 'derive' o 'integrate'