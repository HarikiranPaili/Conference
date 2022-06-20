from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.

@admin.register(EmpMaster)
class ViewAdmin(ImportExportModelAdmin):
    list_display = ('Empid','emp_name','campus','college_code','dept_code','email')
    list_filter = ('campus',)
