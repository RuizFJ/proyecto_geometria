from django.db import models

class Formula(models.Model):
    expression = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    type = models.CharField(max_length=20)  # 'derive' o 'integrate'