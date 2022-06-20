from django.db import models

# Create your models here.
class EmpMaster(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    Empid = models.IntegerField(null=True,blank=True)
    emp_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    phone = models.IntegerField(null=True,blank=True)
    dept_code = models.CharField(max_length=200, null=True, blank=True)
    college_code = models.CharField(max_length=200, null=True, blank=True)
    campus = models.CharField(max_length=200, null=True, blank=True)
