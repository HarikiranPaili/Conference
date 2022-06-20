from django.contrib import admin
from .models import User,UserGroups
from import_export.admin import ImportExportModelAdmin

# Register your models here.
@admin.register(User)
class ViewAdmin(ImportExportModelAdmin):

    list_display = ['id','u_id','username','first_name','email']
    list_filter = ['flag_counter',]
    search_fields = ('username','u_id','email')



class UserGroupsAdmin(admin.ModelAdmin):

    list_display = ['id','user','group','role','is_active','is_default','is_block']
    list_filter = ['group','role']
    search_fields = ('user',)

admin.site.register(UserGroups,UserGroupsAdmin)


