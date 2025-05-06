from django.db import models

class holiday(models.Model):
    holiday_id = models.AutoField(primary_key=True)
    occasion = models.CharField(max_length=100)
    leave_type = models.CharField(max_length=100)
    holiday_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    # updated_by = models.IntegerField()
