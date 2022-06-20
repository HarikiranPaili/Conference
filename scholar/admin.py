from django.contrib import admin
from .models import *
# Register your models here.

class ProposalAdmin(admin.ModelAdmin):
    list_display = ['id','u_id','title']
    list_filter = ['u_id','proposal_status']
admin.site.register(Proposal,ProposalAdmin)






# class ZoomMeetingAdmin(admin.ModelAdmin):
#     list_display = ['userid','reviewers','meeting_start_date','meeting_end_date']
#     list_filter = ['userid','reviewers']
# admin.site.register(ZoomMeeting,ZoomMeetingAdmin)