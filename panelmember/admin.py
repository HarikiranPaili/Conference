from django.contrib import admin
from .models import PanelMember

# Register your models here.

class PanelMemberAdmin(admin.ModelAdmin):
    list_display = ['proposal_id','get_name','assigned_date','panel_status','userid']

    def get_name(self, obj):
        return obj.panelmember_id.username

    get_name.admin_order_field = 'panelmember_id'
    get_name.short_description = 'PanelMember Name'
    list_filter = ['panel_status',]
admin.site.register(PanelMember,PanelMemberAdmin)
