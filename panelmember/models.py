from django.db import models
from scholar.models import *

# Create your models here.
class PanelMember(models.Model):
    class PanelMemberStatus(models.TextChoices):
        PENDING = "PENDING"
        COMPLETED = "COMPLETED"
    id = models.AutoField(primary_key=True, auto_created=True)
    proposal_id = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    userid = models.CharField(max_length=100, null=True, blank=True)
    panelmember_id = models.ForeignKey(User, on_delete=models.CASCADE)
    zoom_meet_link =  models.CharField(max_length=500, null=True, blank=True)
    assigned_date = models.DateTimeField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    panel_status = models.CharField(max_length=20, choices=PanelMemberStatus.choices, default="PENDING")
    avg_score = models.IntegerField(null=True,blank=True)
    panelmember_comments = models.CharField(max_length=1500, null=True, blank=True)
    created_on = models.DateField(null=True, blank=True)
    updated_on = models.DateField(null=True, blank=True)
    flag = models.IntegerField(default=0,null=True,blank=True)

