from django.db import models
from scholar.models import Proposal, User


class Reviewer(models.Model):
    class ReviewerStatus(models.TextChoices):
        PENDING = "PENDING"
        ACCEPTED = "ACCEPTED"
        POSTER = "POSTER"
        REJECTED = "REJECTED"

    proposal_id = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    reviewer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewer_comments = models.CharField(max_length=1000, null=True, blank=True)
    assigned_date = models.DateTimeField(null=True, blank=True)
    reviewer_status = models.CharField(max_length=20, choices=ReviewerStatus.choices, default="PENDING")
    userid = models.CharField(max_length=100, null=True, blank=True)
    created_on = models.DateField(null=True, blank=True)
    updated_on = models.DateField(null=True, blank=True)


class ReviewerQuestions(models.Model):
    id = models.AutoField(primary_key=True)
    ques = models.CharField(max_length=100)
    flag = models.BooleanField(default=1)


class ReviewerScores(models.Model):
    id = models.AutoField(primary_key=True)
    proposal_id = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    reviewer_id = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    ques = models.ForeignKey(ReviewerQuestions, on_delete=models.CASCADE)
    score = models.IntegerField(null=False, default=0)
