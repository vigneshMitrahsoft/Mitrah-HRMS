from django.db import models

# Create your models here.


class shift_type(models.Model):
    shift_type_id = models.BigAutoField(primary_key=True)
    shift_type_name = models.CharField(max_length=100)
    description = models.CharField(max_length=400, blank = True)
    is_active = models.BooleanField(default = True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True, blank = True)
    created_by = models.IntegerField()
    updated_at = models.DateTimeField(auto_now = True, blank = True)
    updated_by = models.IntegerField()

    class Meta:
        db_table = 'shift_type'