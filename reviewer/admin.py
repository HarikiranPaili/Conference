from django.contrib import admin
from .models import *


# Register your models here.
class ReviewerAdmin(admin.ModelAdmin):
    list_display = ['proposal_id', 'reviewer_id', 'assigned_date', 'reviewer_status', 'userid']
    list_filter = ['reviewer_status', ]


admin.site.register(Reviewer, ReviewerAdmin)


class ReviewerScore(admin.ModelAdmin):
    list_display = ['proposal_id', 'reviewer_id', 'ques', 'score', ]
    list_filter = ['ques', ]


admin.site.register(ReviewerScores, ReviewerScore)


class ReviewerQuestion(admin.ModelAdmin):
    list_display = ['id', 'ques', 'flag',]
    list_filter = ['id', ]


admin.site.register(ReviewerQuestions, ReviewerQuestion)
