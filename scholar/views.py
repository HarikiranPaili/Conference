from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from copyleaks.copyleaks import Copyleaks, Products
from copyleaks.exceptions.command_error import CommandError
from copyleaks.models.submit.document import FileDocument, UrlDocument, OcrFileDocument
from copyleaks.models.submit.properties.scan_properties import ScanProperties
from copyleaks.models.export import *
from reviewer.models import *
from usermanagement.models import *
from django.template.loader import render_to_string, get_template
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import random
from io import BytesIO
from .models import User, Proposal
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test
import pandas as pd
from django.db.models import Value
from django.db.models.functions import Lower, Replace
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Q

EMAIL_ADDRESS = 'nmaddine@gitam.edu'
KEY = 'abc54f93-9ad4-4f5c-ad1d-e0d3550498e6'
PRODUCT = Products.EDUCATION  #BUSINESSES or EDUCATION, depending on your Copyleaks account type.

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):

        if u.is_authenticated:
            if u.groups.filter(name__in=group_names):
                return True
        return False
    return user_passes_test(in_groups)


def index(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    else:
        return render(request, 'login.html')

def login_view(request):
    login(request, request.user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect('/dashboard')


def login_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({'data': 1, 'failed': 0})
    else:
        if 'failed' in request.session:
            messages.error(request, 'You have no access to login')
            del request.session['failed']
            return JsonResponse({'data': 1, 'failed': 1})
        else:
            return JsonResponse({'data': 0, 'failed': 0})

@group_required('Admin')
def admin(request):
    proposal = Proposal.objects.all().values('id', 'title', 'proposal_status', 'documents', 'plagarism_score',
                                             'u_id__campus', 'u_id__institution', 'u_id__department', 'doc_scanid',
                                             'plagarism_doc','supervisor_status')
    total = Proposal.objects.all().count()
    a_reviewer_pending = Proposal.objects.filter(proposal_status=0,supervisor_status='Approved').count()
    pending_with_reviewer = Proposal.objects.filter(proposal_status=1).count()
    a_panel_pending = Proposal.objects.filter(proposal_status=2).count()
    pending_with_panelmember = Proposal.objects.filter(proposal_status=3).count()
    a_poster = Proposal.objects.filter(proposal_status=20).count()
    completed = Proposal.objects.filter(proposal_status=4).count()
    rejected = Proposal.objects.filter(Q(proposal_status=-1) | Q(supervisor_status='Rejected')).count()
    reviewer = User.objects.filter(groups=2).values()
    panelmem = User.objects.filter(groups=3).values()
    context = dict()
    context['admin'] = proposal
    context['total'] = total
    context['a_reviewer_pending'] = a_reviewer_pending

    context['a_poster'] = a_poster
    context['a_panel_pending'] = a_panel_pending
    context['pending_with_reviewer'] = pending_with_reviewer
    context['pending_with_panelmember'] = pending_with_panelmember
    context['completed'] = completed
    context['rejected'] = rejected
    context['reviewer'] = reviewer
    context['panelmem'] = panelmem

    return render(request, 'admin.html', context=context)

def close(request):
    return render(request, 'close.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def failed(request):
    messages.error(request, 'You have no access to login')
    return redirect('/')


def add_proposal(request):
    if request.method == 'POST':
        title = request.POST['title']
        logout(request)
        return redirect('dashboard.html')


@login_required(redirect_field_name=None)
def dashboard(request):
    uid = User.objects.get(id=request.user.id)
    #user = UserGroups.objects.get(user=uid)
    data = UserGroups.objects.filter(user=uid).values('id','role', 'group_id__name','is_default','is_active')
    print(data)
    role = data.filter(is_default=True)
    if role[0]['role'] == 'Scholar':
        proposal = Proposal.objects.filter(u_id=request.user.id)
        context = dict()
        context['data'] = proposal
        return render(request, 'dashboard.html', context)
    elif role[0]['role'] == 'Reviewer':
        return redirect('reviewer')
    elif role[0]['role'] == 'PanelMember':
        return redirect('panelmember')
    elif role[0]['role'] == 'Admin':
    #elif user.group == 'Admin':
        return redirect('admin')
    return redirect("/")

@login_required
def get_res(request):
    prop = Proposal.objects.filter(u_id=request.user.id, notify=0, status='completed')
    proposal = prop.values()
    data ={}
    if proposal:
        proposallist = list(proposal)
        for i in range(len(proposallist)):
            data[i]={}
            data[i]['doc_scanid'] = proposallist[i]['doc_scanid']
            data[i]['plagiarism'] = proposallist[i]['plagiarism']
            data[i]['title'] = proposallist[i]['title']
        prop.update(notify=1)
        return JsonResponse({'data': data, 'stat': 1})
    else:
        return JsonResponse({'stat': 0})

@login_required
def get_title(request):
    if request.method == 'GET':
        title = request.GET['data']
        if Proposal.objects.filter(title=title).exists():
            return JsonResponse({'data': 1})
        else:
            # no object satisfying query exists
            return JsonResponse({'data': 0})

@login_required
def copy_leaks(request):
    # try:
    #     auth_token = Copyleaks.login(EMAIL_ADDRESS, KEY)
    # except CommandError as ce:
    #     return JsonResponse({'data': 0})
    if request.method == 'POST':
        scan_id = random.randint(100, 1000000)
        title = request.POST['paperTitle']
        abstract = request.POST['paperAbstract']
        summary = request.POST['paperSummary']
        keypoints = request.POST['paperKeyPoints']
        p_score = request.POST['similarity']
        file = request.FILES['paperfile']
        pdoc = request.FILES['reportfile']
        title_lower = ''.join(i.lower() for i in title.split())

        s =  Proposal.objects.annotate(
            lowered_nospace_name=Lower(Replace('title', Value(' '), Value('')))
        ).filter(
            lowered_nospace_name=title_lower
        )
        print(s)
        if s:
            messages.error(request, 'Title already exists!')
            return redirect('/dashboard')
        else:
            user = User.objects.get(id=request.user.id)
            obj, created = Proposal.objects.get_or_create(title=title, u_id=user)
            obj.title = title
            obj.abstract = abstract
            obj.documents = file
            obj.plagarism_doc = pdoc
            obj.doc_scanid = scan_id
            obj.plagarism_score = p_score
            obj.notify = 0
            obj.summary = summary
            obj.keypoints = keypoints
            obj.proposal_date = datetime.now()
            obj.save()
            if int(p_score) >= 21:
                Proposal.objects.filter(id=obj.id).update(proposal_status=-1,rejected_by=1)
                messages.error(request, 'Your paper has been Auto rejected!')
                return redirect('/dashboard')

            else:
                pass
            context = dict()
            context['paper_title'] = title
            context['scholar_name'] = request.user.username
            email_list = []
            email_list.append(request.user.email)
            message = get_template('scholar_confirm_submit.html').render(context)
            msg = EmailMessage(
                'Re: Confirmation Email for Scholar Confrence to the paper - ' + title,
                message,
                'gears_support@gitam.edu',
                email_list,
            )
            msg.content_subtype = "html"
            msg.send()

            messages.success(request, 'Your paper has been submitted! and confirmation sent to your email!')

            # sending mail to supervisor

            context = dict()
            context['paper_title'] = title
            context['scholar_name'] = request.user.username
            context['pk'] = obj.id
            email_list = []
            email_list.append(request.user.supervisor_email)

            message = get_template('supervisor_mail.html').render(context)
            msg = EmailMessage(
                'Re: Confirmation Email for Scholar Confrence to the paper - ' + title,
                message,
                'gears_support@gitam.edu',
                email_list,
            )
            msg.content_subtype = "html"
            msg.send()
            return redirect('/dashboard')
    else:
        messages.success(request, 'Something went wrong! Please try again later.')
        return redirect('/dashboard')

def superv_approval(request,pk):
    try:
        object = Proposal.objects.get(id=pk,supervisor_status='Pending')
        object.supervisor_status = 'Approved'
        object.save()
        return  HttpResponse("You Approved the Application, you may close this page now")
    except:
        return HttpResponse("Application status changed")
def superv_reject(request,pk):
    try:
        object = Proposal.objects.get(id=pk,supervisor_status='Pending')
        object.supervisor_status = 'Rejected'
        object.save()
        return  HttpResponse("You Rejected the Application, you may close this page now")
    except:
        return HttpResponse("Application status changed")

@login_required
def scholar_edited(request):

    if request.method == 'POST':

        title = request.POST.get('paperTitle',False)
        pid = request.POST.get('pid',False)
        abstract = request.POST.get('paperAbstract',False)
        summary = request.POST.get('paperSummary',False)
        keypoints = request.POST.get('paperKeyPoints',False)
        p_score = request.POST.get('similarity',False)
        file = request.FILES.get('paperfile',False)
        pdoc = request.FILES.get('reportfile',False)

        if int(p_score) >= 21:
            Proposal.objects.filter(id=pid).update(proposal_status=-1, rejected_by=1)
            messages.error(request, 'Your paper has been Auto rejected!')
            return redirect('/dashboard')
        else:

            Proposal.objects.filter(id=pid).update(title=title,abstract=abstract,summary=summary,

                                              keypoints=keypoints,plagarism_score=p_score)
        if file:
            obj, created = Proposal.objects.get_or_create(id=pid)
            obj.documents = file
            obj.save()

        if pdoc:
            obj, created = Proposal.objects.get_or_create(id=pid)
            obj.plagarism_doc = pdoc
            obj.save()


        messages.success(request, 'Your paper Changes has been Updated')
        return redirect('/dashboard')

    messages.success(request, 'Something went wrong! Please try again later.')
    return redirect('/dashboard')

@csrf_exempt
def webhook(request, status, scanid):
    if status == "{completed}":
        payload = json.loads(request.body)
        obj, created = Proposal.objects.get_or_create(doc_scanid=scanid)
        obj.status = 'completed'
        obj.plagiarism = payload['results']['score']['aggregatedScore']
        obj.save()
        return HttpResponse('ok')
    else:
        return HttpResponse('failed')
