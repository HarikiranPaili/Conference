from django.db import models
from usermanagement.models import User
import json

# Create your models here.

Status ={
    ('Pending','Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
}

class Proposal(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    u_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1500, null=True, blank=True)
    abstract = models.CharField(max_length=1500, null=True, blank=True)
    summary = models.CharField(max_length=1500, null=True, blank=True)
    keypoints = models.CharField(max_length=1500, null=True, blank=True)
    documents = models.FileField(upload_to="proposal_documents/", null=True,blank=True)
    plagarism_doc = models.FileField(upload_to="plagarism/",null=True, blank=True)
    re_documents = models.FileField(upload_to="reup_documents/", blank=True,null=True)
    plagarism_score = models.IntegerField(null=True, blank=True)
    doc_scanid = models.IntegerField(null=True, blank=True)
    proposal_date = models.DateField(null=True, blank=True)
    plagiarism = models.CharField(max_length=50,null=True, blank=True)
    status = models.CharField(max_length=50,null=True, blank=True)
    re_upload = models.BooleanField(default=False,null=True, blank=True)
    proposal_status = models.IntegerField(default=0,null=True, blank=True)
    total_panel_count = models.IntegerField(default=0,null=True, blank=True)
    result_panel_count = models.IntegerField(default=0,null=True, blank=True)
    rejected_by = models.IntegerField(null=True, blank=True)
    avg_score = models.FloatField(null=True, blank=True)
    supervisor_status = models.CharField(max_length=10,choices=Status,default='Pending')


    def __str__(self):
        return self.title


class ZoomMeeting(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    userid = models.CharField(max_length=100, null=True, blank=True)
    reviewers = models.CharField(max_length=500, null=True, blank=True)
    meetingid = models.CharField(max_length=500, null=True, blank=True)
    meeting_start_date = models.DateTimeField(null=True,blank=True)
    meeting_end_date = models.DateTimeField(null=True,blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    flag = models.BooleanField(default=False)


    def set_reviewers(self, x):
        self.reviewers = json.dumps(x)

    def get_reviewers(self):
        return json.loads(self.reviewers)



