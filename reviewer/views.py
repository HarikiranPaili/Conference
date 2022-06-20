from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import *
from django.core.mail import EmailMessage
from scholar.views import group_required
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import numpy as np
from django.template.loader import render_to_string, get_template


@group_required('Reviewer')
def reviewer(request):
    data = Reviewer.objects.filter(reviewer_id__id=request.user.id).values('id', 'proposal_id__id',
                                                                           'proposal_id__title', 'reviewer_status',
                                                                           'proposal_id__re_documents',
                                                                           'proposal_id__id')
    questions = ReviewerQuestions.objects.filter(flag=1).values()
    pending = data.filter(reviewer_status='PENDING').count()
    accepted = data.filter(reviewer_status='ACCEPTED').count()
    rejected = data.filter(reviewer_status='REJECTED').count()
    poster = data.filter(reviewer_status='POSTER').count()
    total = data.count()
    context = dict()
    context['data'] = data
    context['questions'] = questions
    context['pending'] = pending
    context['accepted'] = accepted
    context['rejected'] = rejected
    context['poster'] = poster
    context['total'] = total
    return render(request, 'reviewer.html', context)


@login_required
def reviewer_action(request):
    updated = datetime.now()
    id = request.POST['sid']
    pid = request.POST['pid']

    ques = request.POST.getlist('ques[]')
    score = request.POST.getlist('scores[]')
    rcomments = request.POST.get('comments')
    reviewer = Reviewer.objects.get(id=id)
    # print(score)
    proposal = Proposal.objects.get(id=pid)
    for i in range(len(ques)):
        quess = ReviewerQuestions.objects.get(id=ques[i])
        obj, created = ReviewerScores.objects.get_or_create(proposal_id=proposal, reviewer_id=reviewer, ques=quess)
        obj.proposal_id = proposal
        obj.reviewer_id = reviewer
        obj.ques = quess
        obj.score = score[i]
        obj.save()

    scores = np.array(score)
    scores = scores.astype(int)
    status = "REJECTED"
    if scores.sum() >= 15:
        status = "ACCEPTED"
    elif 10 <= scores.sum() < 15:
        status = "POSTER"
    Reviewer.objects.filter(id=id).update(reviewer_status=status, updated_on=updated, reviewer_comments=rcomments)


    if status == "REJECTED":
        Proposal.objects.filter(id=pid).update(proposal_status=-1, rejected_by=2)

        messages.success(request, 'Paper Rejected')
    else:
        if status == "POSTER":
            Proposal.objects.filter(id=pid).update(proposal_status=20)
            applicant_details = Proposal.objects.filter(id=pid).values('u_id__username', 'u_id__email', 'title')
            a_title = applicant_details[0]['title']
            a_email = applicant_details[0]['u_id__email']
            applicant_name = applicant_details[0]['u_id__username']
            Subject = "Poster Presentation for GEARS 2.0"
            title = a_title
            emails = a_email

            Body = "Dear " + applicant_name + ", \n\n" \
                                              "We are glad to inform you that your paper has been approved for Poster Presentation for GEARS 2.0. In this regard, we kindly request you to prepare the Poster according to the regulations attached to this mail." "\n\n" \
                                              "You may contact us at 08912840204  or gears_support@gitam.edu  if you have any questions or need any clarifications on them.\n.\n  Best regards, \nG-Venture Funds Team"
            email = EmailMessage(Subject, Body, to=[emails])
            email.attach_file('poster_guide.pdf')
            email.send()
            return redirect('reviewer')

        else:
            Proposal.objects.filter(id=pid).update(proposal_status=2)
    pdata = Proposal.objects.filter(id=pid).values('u_id_id__username', 'u_id_id__email', 'title')
    scholar_email = pdata[0]['u_id_id__email']
    scholar_name = pdata[0]['u_id_id__username']
    prop_title = pdata[0]['title']
    email_list = [scholar_email]
    context = dict()
    context['scholar_name'] = scholar_name
    context['prop_title'] = prop_title
    if status == "ACCEPTED":
        message = get_template('auto_email_to_scholar_after_reviewer.html').render(context)
    else:
        message = get_template('auto_email_to_scholar_after_reviewerreject.html').render(context)

    msg = EmailMessage(
        'Re: Scholar Paper Status after Reviewer result for' + prop_title,
        message,
        'gears_support@gitam.edu',
        email_list,
    )
    msg.content_subtype = "html"
    msg.send()
    messages.success(request, 'Thank you for the report. Your result has been saved')
    return redirect('reviewer')


@login_required
def email(request, id):
    Subject = "Re: Pending Scholar Reviews"
    pid = Proposal.objects.get(id=id)
    data = Reviewer.objects.filter(proposal_id=pid).values('proposal_id__title', 'reviewer_id__email')

    title = data[0]['proposal_id__title']
    emails = data[0]['reviewer_id__email']

    Body = "Hi Sir/Madam, " \
           "Please review the pending Scholar paper with title" + "  " + title
    email = EmailMessage(Subject, Body, to=[emails])
    email.send()
    messages.success(request, 'Reminder Email sent Successfully')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
