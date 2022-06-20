from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import PanelMember
from scholar.models import *
from scholar.views import group_required
from datetime import datetime
from django.contrib import messages
from django.db.models import Q, F, Avg


# Create your views here.
@group_required('PanelMember')
def panelmember(request):
    data = PanelMember.objects.filter(panelmember_id__id=request.user.id).values('id', 'proposal_id__title',
                                                                                 'panel_status',
                                                                                 'proposal_id__re_documents',
                                                                                 'proposal_id__id',
                                                                                 'assigned_date', 'scheduled_date',
                                                                                 'avg_score')
    pending = data.filter(panel_status='PENDING').count()
    completed = data.filter(panel_status='COMPLETED').count()
    on_hold = data.filter(panel_status='ONHOLD').count()
    total = data.count()
    context = dict()
    context['data'] = data
    context['pending'] = pending
    context['completed'] = completed
    context['on_hold'] = on_hold
    context['total'] = total
    return render(request, 'panelmember.html', context)

@login_required
def panelmember_action(request):
    updated = datetime.now()
    id = request.POST['sid']
    pid = request.POST['prop_id']
    score = request.POST['score']
    remarks = request.POST['remarks']
    PanelMember.objects.filter(id=id).update(avg_score=score, panelmember_comments=remarks, flag=1,
                                             panel_status="COMPLETED", updated_on=updated)
    Proposal.objects.filter(id=pid).update(result_panel_count=F('result_panel_count') + 1)
    panelcount_check = Proposal.objects.filter(id=pid).values('total_panel_count', 'result_panel_count',
                                                              'proposal_status')
    total = panelcount_check[0]['total_panel_count']
    res_count = panelcount_check[0]['result_panel_count']
    if total == res_count:
        propid = Proposal.objects.get(id=pid)
        scores = PanelMember.objects.filter(proposal_id=propid).values('proposal_id__title', 'avg_score').aggregate(
            Avg('avg_score'))
        avg_score = scores['avg_score__avg']
        Proposal.objects.filter(id=pid).update(proposal_status=4, avg_score=avg_score)
    else:
        pass

    messages.success(request, 'Thank you for your Evaluation')
    return redirect('panelmember')

@login_required
def panelmember_edit(request, id):
    id = id
    data = PanelMember.objects.filter(id=id).values('id', 'proposal_id__id', 'proposal_id__title', 'panel_status',
                                                    'proposal_id__re_documents', 'proposal_id__id',
                                                    'assigned_date', 'scheduled_date')
    pid = data[0]['id']
    prop_id = data[0]['proposal_id__id']
    context = dict()
    context['data'] = data
    context['pid'] = pid
    context['prop_id'] = prop_id
    return render(request, 'paneledit.html', context)
