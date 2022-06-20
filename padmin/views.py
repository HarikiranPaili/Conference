from django.shortcuts import render, redirect
from reviewer.models import *
from scholar.models import *
from usermanagement.models import *
from panelmember.models import *
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import EmpMaster
from django.template.loader import render_to_string
from django.contrib.auth.models import Group
from social.apps.django_app.default.models import UserSocialAuth
from django.contrib import messages
import string
import random
from django.db.models import Q, Count, Sum, Avg, StdDev, ExpressionWrapper, FloatField
import pandas as pd
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required


# Create your views here.


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required
def admin_reupload(request):
    if request.method == 'POST':
        document = request.FILES['paperfile']
        pid = request.POST['pid']
        reviewer_id = request.POST['reviewer']

        if reviewer_id:
            rid = User.objects.get(id=reviewer_id)
            reviewer_data = User.objects.filter(id=reviewer_id).values('email', 'username')
            reviewer_email = reviewer_data[0]['email']
            reviewer_name = reviewer_data[0]['username']
            proid = Proposal.objects.get(id=pid)
            prop_data = Proposal.objects.filter(id=pid).values('title')
            prop_title = prop_data[0]['title']
            obj, created = Reviewer.objects.get_or_create(reviewer_id=rid, proposal_id=proid)
            obj.assigned_date = datetime.now()
            obj.created_on = datetime.now()
            obj.save()
        if document:
            obj, created = Proposal.objects.get_or_create(id=pid)
            obj.re_documents = document
            obj.re_upload = True
            obj.proposal_status = 1
            obj.save()

        context = dict()
        context['reviewer_name'] = reviewer_name
        context['prop_title'] = prop_title

        email_list = []
        email_list.append(reviewer_email)
        message = get_template('auto_email_reviewer.html').render(context)
        msg = EmailMessage(
            'Re: Scholar Paper Proposal Review for paper' + prop_title,
            message,
            'gears_support@gitam.edu',
            email_list,
        )
        msg.content_subtype = "html"
        msg.send()
        messages.success(request, 'Assigned to Reviewer Successfully')
        return redirect('admin')
    messages.dager(request, 'Something went wrong! Please try again.')
    return redirect('admin')

@login_required
def addreviewer(request):
    try:
        campus = EmpMaster.objects.all().values('campus').distinct()
        reviewer = Reviewer.objects.all().values('reviewer_id_id__username', 'reviewer_id_id__u_id', 'reviewer_status')
        reviewer_list = User.objects.filter(groups__name='Reviewer').values()

        try:
            rdf = pd.DataFrame(list(reviewer_list))
            rdf = rdf[['username', 'u_id']]
            rdf.rename(columns={'u_id': 'reviewer_id_id__u_id', 'username': 'reviewer_id_id__username'}, inplace=True)
        except:
            rdf = ""

        elist = []
        if reviewer_list:
            if reviewer:
                df = pd.DataFrame(list(reviewer))
                df2 = rdf.merge(df, on=['reviewer_id_id__u_id', 'reviewer_id_id__username'], how='left')
                df = df2
                # print(df)
                total = df[['reviewer_id_id__u_id', 'reviewer_id_id__username']].value_counts()
                tdf = pd.DataFrame(total)
                tdf.columns = [''] * len(tdf.columns)
                tdf = tdf.reset_index()
                tdf.columns = ['Empid', 'emp_name', 'total']
                total = tdf.to_dict(orient="records")
                stat = df[['reviewer_id_id__u_id', 'reviewer_status']].value_counts()
                df2 = pd.DataFrame(stat)
                df2.columns = [''] * len(df2.columns)
                df2 = df2.reset_index()
                df2.columns = ['Empid', 'status', 'count']
                # print(df2)
                status = df2.to_dict(orient="records")
                print(status)

                for i in total:
                    for j in status:
                        if i['Empid'] == j['Empid']:
                            if j['status'] == 'ACCEPTED':
                                i['Accepted'] = j['count']
                            elif j['status'] == 'REJECTED':
                                i['Rejected'] = j['count']
                            elif j['status'] == 'PENDING':
                                i['Pending'] = j['count']
                            elif j['status'] == 'POSTER':
                                i['Poster'] = j['count']
                    elist.append(i)

                not_assigned = 0

                for i in elist:
                    count = 0
                    if 'Accepted' in i:
                        count += i['Accepted']
                    if 'Rejected' in i:
                        count += i['Rejected']
                    if 'Pending' in i:
                        count += i['Pending']
                    if 'Poster' in i:
                        count += i['Poster']
                    if count < i['total']:
                        i['total'] = count
                        not_assigned += 1

                context = dict()
                total = len(elist)

                context['total'] = total
                context['assigned'] = total - not_assigned
                context['not_assigned'] = not_assigned
                context['campus'] = campus
                context['data'] = elist

                return render(request, 'addreviewer.html', context)
            else:
                temp_df = pd.DataFrame(reviewer_list)
                print(temp_df.columns)
                temp_df.rename(columns={'u_id': 'Empid', 'username': 'emp_name'}, inplace=True)
                # temp_df.columns = ['Empid', 'emp_name']
                total = reviewer_list.count()
                temp_df['total'] = 0
                temp_df = temp_df.to_dict(orient="records")

                context = dict()
                context['total'] = total
                context['assigned'] = 0
                context['not_assigned'] = total
                context['campus'] = campus
                context['data'] = temp_df
                return render(request, 'addreviewer.html', context)

        else:
            context = dict()
            context['campus'] = campus
            context['data'] = elist
            return render(request, 'addreviewer.html', context)


    except:
        messages.success(request, 'No data in the reviewer.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def addpanelmember(request):
    campus = EmpMaster.objects.all().values('campus').distinct()
    pdata = PanelMember.objects.all().values('panelmember_id_id__username', 'panelmember_id_id__u_id', 'panel_status')
    panel_list = User.objects.filter(groups__name='PanelMember').values()
    try:
        rdf = pd.DataFrame(list(panel_list))
        rdf = rdf[['username', 'u_id']]
        rdf.rename(columns={'u_id': 'panelmember_id_id__u_id', 'username': 'panelmember_id_id__username'}, inplace=True)
    except:
        rdf = ""

    elist = []
    if panel_list:
        if pdata:
            df = pd.DataFrame(list(pdata))
            df2 = rdf.merge(df, on=['panelmember_id_id__u_id', 'panelmember_id_id__username'], how='left')
            df = df2
            total = df[['panelmember_id_id__u_id', 'panelmember_id_id__username']].value_counts()
            tdf = pd.DataFrame(total)
            tdf.columns = [''] * len(tdf.columns)
            tdf = tdf.reset_index()
            tdf.columns = ['Empid', 'emp_name', 'total']
            total = tdf.to_dict(orient="records")
            # print(total)
            stat = df[['panelmember_id_id__u_id', 'panel_status']].value_counts()
            df2 = pd.DataFrame(stat)
            df2.columns = [''] * len(df2.columns)
            df2 = df2.reset_index()
            df2.columns = ['Empid', 'status', 'count']
            status = df2.to_dict(orient="records")
            for i in total:
                for j in status:
                    if i['Empid'] == j['Empid']:
                        if j['status'] == 'COMPLETED':
                            i['COMPLETED'] = j['count']
                        elif j['status'] == 'PENDING':
                            i['Pending'] = j['count']
                elist.append(i)
            # print(elist)
            not_assigned = 0
            for i in elist:
                count = 0
                if 'COMPLETED' in i:
                    count += i['COMPLETED']
                if 'Pending' in i:
                    count += i['Pending']
                if count < i['total']:
                    i['total'] = 0
                    not_assigned += 1
            context = dict()
            total = len(elist)
            context['total'] = total
            context['assigned'] = total - not_assigned
            context['not_assigned'] = not_assigned
            context['campus'] = campus
            context['data'] = elist

            return render(request, 'addpanelmember.html', context)
        else:
            temp_df = pd.DataFrame(panel_list)
            print(temp_df.columns)
            temp_df.rename(columns={'u_id': 'Empid', 'username': 'emp_name'}, inplace=True)
            #temp_df.columns = ['Empid', 'emp_name']
            total = panel_list.count()
            temp_df['total'] = 0
            temp_df = temp_df.to_dict(orient="records")


            context = dict()
            context['total'] = total
            context['assigned'] = 0
            context['not_assigned'] = total
            context['campus'] = campus
            context['data'] = temp_df
            return render(request, 'addpanelmember.html', context)
    else:

        context = dict()
        context['total'] = 0
        context['assigned'] = 0
        context['not_assigned'] = 0
        context['campus'] = campus
        context['data'] = elist
        return render(request, 'addpanelmember.html', context)

@login_required
def add_new_reviewer(request):
    if request.method == "POST":
        campus = request.POST['campus']
        inst = request.POST['inst']
        dept = request.POST['dept']
        Empid = request.POST['Empid']
        data = EmpMaster.objects.filter(Empid=Empid).values()
        email = data[0]['email']
        emp_name = data[0]['emp_name']
        # print(emp_name)
        password = "pbkdf2_sha256$260000$JAXTqy0R4LAxkAyIZkv3RL$ZGd+G6tcTnJac58M8V8TtOKvYBcj0d8X8bL3oJjYXVk="
        obj, created = User.objects.get_or_create(email=email, u_id=Empid)
        obj.password = password
        obj.username = emp_name
        obj.first_name = emp_name
        obj.campus = campus
        obj.institution = inst
        obj.department = dept
        obj.u_id = Empid
        obj.is_staff = True
        obj.save()

        gdata = UserSocialAuth.objects.filter(uid=email).values()
        if gdata:
            pass
        else:
            obj1, created = UserSocialAuth.objects.get_or_create(user_id=obj.id, uid=email)
            obj1.provider = 'google-oauth2'
            obj1.uid = email
            obj1.extra_data = {}
            obj1.save()

        group_id = Group.objects.get(id=2)

        usergroup_exits = UserGroups.objects.filter(user=obj).values()

        if usergroup_exits:
            obj2, created = UserGroups.objects.get_or_create(group=group_id, user=obj)
            obj2.role = "Reviewer"
            obj2.is_active = True
            obj2.is_default = False
            obj2.is_block = False
            obj2.save()
        else:
            obj2, created = UserGroups.objects.get_or_create(group=group_id, user=obj)
            obj2.role = "Reviewer"
            obj2.is_active = True
            obj2.is_default = True
            obj2.is_block = False
            obj2.save()
        messages.success(request, 'Changes successfully saved.')
        return redirect('addreviewer')

@login_required
def add_new_panelmember(request):
    if request.method == "POST":
        campus = request.POST['campus']
        inst = request.POST['inst']
        dept = request.POST['dept']
        Empid = request.POST['Empid']
        data = EmpMaster.objects.filter(Empid=Empid).values()
        email = data[0]['email']
        emp_name = data[0]['emp_name']

        password = "pbkdf2_sha256$260000$JAXTqy0R4LAxkAyIZkv3RL$ZGd+G6tcTnJac58M8V8TtOKvYBcj0d8X8bL3oJjYXVk="
        obj, created = User.objects.get_or_create(email=email, u_id=Empid)
        obj.password = password
        obj.username = emp_name
        obj.first_name = emp_name
        obj.campus = campus
        obj.institution = inst
        obj.department = dept
        obj.u_id = Empid
        obj.is_staff = True
        obj.save()

        obj1, created = UserSocialAuth.objects.get_or_create(user_id=obj.id, uid=email)
        obj1.provider = 'google-oauth2'
        obj1.uid = email
        obj1.extra_data = {}
        obj1.save()

        group_id = Group.objects.get(id=3)

        usergroup_exits = UserGroups.objects.filter(user=obj).values()

        if usergroup_exits:
            obj2, created = UserGroups.objects.get_or_create(group=group_id, user=obj)
            obj2.role = "PanelMember"
            obj2.is_active = True
            obj2.is_default = False
            obj2.is_block = False
            obj2.save()
        else:
            obj2, created = UserGroups.objects.get_or_create(group=group_id, user=obj)
            obj2.role = "PanelMember"
            obj2.is_active = True
            obj2.is_default = True
            obj2.is_block = False
            obj2.save()

        messages.success(request, 'Panelmember added successfully.')
        return redirect('addpanelmember')

@login_required
def add_external_panelmember(request):
    if request.method == "POST":
        designation = request.POST['designation']
        inst = request.POST['inst']
        dept = request.POST['dept']
        Empid = "EXTN-" + id_generator()
        email = request.POST['email']
        phone = request.POST['phone']
        emp_name = request.POST['name']
        password = "pbkdf2_sha256$260000$JAXTqy0R4LAxkAyIZkv3RL$ZGd+G6tcTnJac58M8V8TtOKvYBcj0d8X8bL3oJjYXVk="
        obj, created = User.objects.get_or_create(email=email)
        obj.password = password
        obj.username = emp_name
        obj.first_name = emp_name
        obj.institution = inst
        obj.phone = phone
        obj.department = dept
        obj.u_id = Empid
        obj.designation = designation
        obj.is_staff = True
        obj.save()

        obj1, created = UserSocialAuth.objects.get_or_create(user_id=obj.id, uid=email)
        obj1.provider = 'google-oauth2'
        obj1.uid = email
        obj1.extra_data = {}
        obj1.save()

        group_id = Group.objects.get(id=3)
        obj2, created = UserGroups.objects.get_or_create(group=group_id, user=obj)
        obj2.role = "PanelMember"
        obj2.is_active = True
        obj2.is_default = True
        obj2.is_block = False
        obj2.save()
        messages.success(request, 'Changes successfully saved.')
        return redirect('addpanelmember')

@login_required
def selected_campus(request):
    if request.method == "GET":
        campus = request.GET.get("campus")
        print(campus)
        inst = EmpMaster.objects.filter(campus=campus).values('college_code').distinct()
        inst = inst.exclude(college_code__in=["GIRLSHOSTEL", "BOYSHOSTEL"])
        inst = inst.filter(college_code__in=["GIT", "CAO", "GIS", "GIM", "GSGS", "GIP", "GSL",
                                             "GST", "GSS", "GHBS", "GSHSS", "GSHS", "HBS", "GSP", "GST", "GSS", "GSBB",
                                             "GSHSS","SMS"])
        Context = dict()
        Context['inst'] = inst
        html_form = render_to_string('inst.html', Context, request=request)
        return JsonResponse({'html_form': html_form})
    return JsonResponse({'html_form': "no data"})

@login_required
def selected_inst(request):
    if request.method == "GET":
        inst = request.GET.get("inst")
        campus = request.GET.get("campus")
        dept = EmpMaster.objects.filter(college_code=inst, campus=campus).values('dept_code').distinct()
        Context = dict()
        Context['dept'] = dept
        html_form = render_to_string('dept.html', Context, request=request)
        return JsonResponse({'html_form': html_form})
    return JsonResponse({'html_form': "no data"})


def selected_dept(request):
    if request.method == "GET":
        dept = request.GET.get("dept")
        inst = request.GET.get("inst")
        campus = request.GET.get("campus")
        Empid = EmpMaster.objects.filter(dept_code=dept, campus=campus, college_code=inst).values('Empid',
                                                                                                  'emp_name').distinct()
        print(Empid)
        Context = dict()
        Context['Empid'] = Empid
        html_form = render_to_string('Empid.html', Context, request=request)
        return JsonResponse({'html_form': html_form})
    return JsonResponse({'html_form': "no data"})

@login_required
def selected_results(request):
    if request.method == "GET":
        campus = request.GET.get("campus")
        inst = request.GET.get("inst")
        dept = request.GET.get("dept")
        ay = request.GET.get("ay")
        filtered = Proposal.objects.filter(u_id_id__campus=campus, u_id_id__institution=inst, u_id_id__department=dept,
                                           proposal_date__year=ay,proposal_status=4).values('u_id_id__u_id', 'u_id_id__first_name',
                                                                          'u_id_id__department',
                                                                          'u_id_id__campus', 'u_id_id__institution',
                                                                          'proposal_date', 'title', 'avg_score')

        Context = dict()
        Context['filtered'] = filtered
        html_form = render_to_string('selected_results.html', Context, request=request)
        return JsonResponse({'data': html_form})
    return JsonResponse({'html_form': "no data"})

@login_required
def send_bulk_email(request, Empid, role):
    Empid = Empid
    Subject = "Re:Reminder for Pending Scholar Reviews"

    if role == "reviewer":
        data = Reviewer.objects.filter(reviewer_id_id__u_id=Empid, reviewer_status="PENDING").values(
            'reviewer_id_id__username', 'proposal_id__title', 'reviewer_id_id__email')
        # print(data)
        df = pd.DataFrame(list(data))
        reviewer_email = df['reviewer_id_id__email'].drop_duplicates().to_list()
        reviewer_name = df['reviewer_id_id__username'].drop_duplicates().to_list()
        prop_titles = df['proposal_id__title'].drop_duplicates().to_list()
    else:
        data = PanelMember.objects.filter(panelmember_id_id__u_id=Empid, panel_status="PENDING").values(
            'panelmember_id_id__username', 'proposal_id__title', 'panelmember_id_id__email')
        # print(data)
        df = pd.DataFrame(list(data))
        reviewer_email = df['panelmember_id_id__email'].drop_duplicates().to_list()
        reviewer_name = df['panelmember_id_id__username'].drop_duplicates().to_list()
        prop_titles = df['proposal_id__title'].drop_duplicates().to_list()

    context = dict()
    context['reviewer_name'] = reviewer_name[0]
    context['prop_title'] = prop_titles

    message = get_template('auto_email_reviewer.html').render(context)
    msg = EmailMessage(
        'Re: Gentle Reminder for Scholar Paper Proposal Review',
        message,
        'gears_support@gitam.edu',
        reviewer_email,
    )
    msg.content_subtype = "html"
    msg.send()

    if role == "reviewer":
        messages.success(request, 'Remainder sent Successfully!!')
        return redirect('addreviewer')

    else:
        messages.success(request, 'Remainder sent Successfully!!')
        return redirect('addpanelmember')
    return redirect('addpanelmember')

@login_required
def panel_upload(request):
    if request.method == 'POST':
        ids = request.POST['ids']
        sdate = request.POST['sdate']
        zmeet = request.POST['zmeet']
        panelmember = request.POST.getlist('panelmember')
        total_panelmembers = len(panelmember)
        ids = ids.split(',')
        # print(ids)
        # print(panelmember)
        # print(sdate)
        # print(zmeet)
        today = datetime.now()

        for i in ids:
            pid = Proposal.objects.get(id=i)
            ptitle = Proposal.objects.filter(id=i).values('title','u_id_id__email','u_id_id__username')

            Proposal.objects.filter(id=i).update(total_panel_count=total_panelmembers)
            for j in panelmember:
                uid = User.objects.get(id=j)
                udata = User.objects.filter(id=j).values('email', 'username')
                obj, created = PanelMember.objects.get_or_create(panelmember_id=uid, proposal_id=pid)
                obj.zoom_meet_link = zmeet
                obj.assigned_date = today
                obj.scheduled_date = sdate
                obj.created_on = today
                obj.panel_status = "PENDING"
                obj.save()
                Proposal.objects.filter(id=i).update(proposal_status=3)

                context = dict()
                context['panelmember'] = udata[0]['username']
                context['ptitle'] = ptitle[0]['title']
                context['semail'] = ptitle[0]['u_id_id__email']
                context['sname'] = ptitle[0]['u_id_id__username']
                context['zmeet'] = zmeet
                context['sdate'] = sdate

                email_list = []
                email_list.append(udata[0]['email'])
                message = get_template('auto_email_panelmember.html').render(context)
                msg = EmailMessage(
                    'Re: Scholar Confrence for paper' + ptitle[0]['title'],
                    message,
                    'gears_support@gitam.edu',
                    email_list,
                )
                msg.content_subtype = "html"
                msg.send()

                semail_list = []
                semail_list.append(ptitle[0]['u_id_id__email'])
                message = get_template('auto_email_scholar_panelselect.html').render(context)
                msg = EmailMessage(
                    'Re: Scholar Confrence Status for paper ' + ptitle[0]['title'],
                    message,
                    'gears_support@gitam.edu',
                    semail_list,
                )
                msg.content_subtype = "html"
                msg.send()


        messages.success(request, 'Assigned to PanelMember Successfully and Sent Email')


        return redirect('admin')
    messages.error(request, 'Something went wrong! Please Try again later.')
    return redirect('admin')

@login_required
def add_scholars(request):
    data = pd.read_excel('PHD Student details.xlsx', sheet_name="2019")
    data.drop_duplicates(inplace=True, keep='last', subset=['MAIL ID'])
    group_id = Group.objects.all().values()
    # print(group_id)
    password = "pbkdf2_sha256$260000$JAXTqy0R4LAxkAyIZkv3RL$ZGd+G6tcTnJac58M8V8TtOKvYBcj0d8X8bL3oJjYXVk="
    for i in range(len(data)):
        username = data.iloc[i]['U ID']
        email = data.iloc[i]['MAIL ID']
        Empid = data.iloc[i]['U ID']
        obj, created = User.objects.get_or_create(email=email, u_id=Empid)
        obj.password = password
        obj.username = username
        obj.email = email
        obj.first_name = data.iloc[i]['FIRST NAME']
        obj.institution = data.iloc[i]['INSITITUTE']
        if not pd.isna(data.iloc[i]['PHONE ']):
            obj.phone = data.iloc[i]['PHONE ']
        obj.department = data.iloc[i]['DEPARTMENT ']
        obj.u_id = Empid
        obj.designation = "Scholar"
        obj.is_staff = False
        obj.save()

        obj1, created = UserSocialAuth.objects.get_or_create(user_id=obj.id, uid=email)
        obj1.provider = 'google-oauth2'
        obj1.uid = email
        obj1.extra_data = {}
        obj1.save()

        group_id = Group.objects.get(id=4)
        obj2, created = UserGroups.objects.get_or_create(group=group_id, user=obj)
        obj2.role = "Scholar"
        obj2.is_active = True
        obj2.is_default = True
        obj2.is_block = False
        obj2.save()
    return redirect('/')

@login_required
def results(request):
    campus = EmpMaster.objects.all().values('campus').distinct()
    result = Proposal.objects.filter(proposal_status=4).values('u_id_id__u_id', 'u_id_id__first_name',
                                                               'u_id_id__department',
                                                               'u_id_id__campus', 'u_id_id__institution',
                                                               'proposal_date', 'title', 'avg_score')
    context = dict()
    context['result'] = result
    context['campus'] = campus
    return render(request, 'result.html', context)

@login_required
def scholar_view(request, id):
    pid = id
    pdata = Proposal.objects.filter(id=pid).values('title', 'u_id_id__username', 'u_id_id__campus','u_id_id__email','u_id_id__phone',
                                                   'u_id_id__institution', 'u_id_id__department', 'abstract',
                                                   'documents', 'plagarism_score', 'keypoints', 'proposal_date',
                                                   'summary', 'avg_score', 'proposal_status')
    reviewer_data = Reviewer.objects.filter(proposal_id_id=pid).values('reviewer_id_id', 'reviewer_id_id__username',
                                                                       'reviewer_comments', 'reviewer_status',
                                                                       'updated_on')
    panel_data = PanelMember.objects.filter(proposal_id_id=pid).values('panelmember_id_id',
                                                                       'panelmember_id_id__username',
                                                                       'panelmember_comments', 'avg_score',
                                                                       'panel_status', 'updated_on')
    scores = ReviewerScores.objects.filter(proposal_id=pid).values('score', 'ques_id__ques')
    if reviewer_data:
        rdata = reviewer_data
    else:
        rdata = ""
    if panel_data:
        paneldata = panel_data

    else:
        paneldata = ""
    summary = pdata[0]['summary']
    abstract = pdata[0]['abstract']
    title = pdata[0]['title']
    keypoints = pdata[0]['keypoints']

    avg_score = pdata[0]['avg_score']
    pstatus = pdata[0]['proposal_status']
    context = dict()
    context['data'] = pdata
    context['rdata'] = rdata
    context['paneldata'] = paneldata
    context['summary'] = summary
    context['title'] = title
    context['scores'] = scores
    context['keypoints'] = keypoints
    context['abstract'] = abstract
    context['pstatus'] = pstatus
    context['avg_score'] = avg_score
    return render(request, 'scholarview.html', context)

@login_required
def admin_reviewer_document(request,id):
    pid = Proposal.objects.get(id=id)
    data = Reviewer.objects.filter(proposal_id=pid).values('id','proposal_id__title', 'reviewer_id__u_id', 'reviewer_id__username',)
    pdoc = Proposal.objects.filter(id=id).values('re_documents')
    reviewer = User.objects.filter(groups=2).values()
    context = dict()
    context['data'] = data
    context['reviewer'] = reviewer
    context['pid'] = id
    context['rid'] = data[0]['id']
    context['document'] = pdoc[0]['re_documents']
    return render(request,'edit_doc.html',context)

@login_required
def change_reviewer_document(request):
    if request.method == 'POST':
        document = request.FILES.get('paperfile',False)
        pid = request.POST['pid']
        rid = request.POST['rid']
        reviewer_id = request.POST.get('reviewer',False)

        if reviewer_id:
            reviewer_id = User.objects.get(id=reviewer_id)
            Reviewer.objects.filter(id=rid).update(reviewer_id=reviewer_id)

        if document:
            obj, created = Proposal.objects.get_or_create(id=pid)
            obj.re_documents = document
            obj.save()

        pro_title = Proposal.objects.filter(id=pid).values('title')
        reviewer_name = Reviewer.objects.filter(id=rid).values('reviewer_id__username','reviewer_id__email')
        context = dict()

        context['reviewer_name'] = reviewer_name[0]['reviewer_id__username']
        context['prop_title'] = pro_title[0]['title']

        email_list = []
        email_list.append(reviewer_name[0]['reviewer_id__email'])
        message = get_template('auto_email_reviewer.html').render(context)
        msg = EmailMessage(
            'Re: Scholar Paper Proposal Review for paper' + pro_title[0]['title'],
            message,
            'gears_support@gitam.edu',
            email_list,
        )
        msg.content_subtype = "html"
        msg.send()
        messages.success(request, 'Reviewer Added Successfully')
        return redirect('admin')
    messages.dager(request, 'Something went wrong! Please try again.')
    return redirect('admin')

@login_required
def reviewer_status(request,id):
    data = Reviewer.objects.filter(reviewer_id_id__u_id=id).values('proposal_id_id__title','proposal_id_id__proposal_date','proposal_id_id__u_id_id__username','proposal_id_id__u_id_id__phone','proposal_id_id__u_id_id__email',
                                                                   'reviewer_id_id__u_id','reviewer_id_id__username','reviewer_id_id__phone','reviewer_id_id__email',
                                                                   'reviewer_status','assigned_date','updated_on','reviewer_comments')
    print(data)
    context = dict()
    context['data'] = data
    context['reviewer'] = data[0]['reviewer_id_id__username']
    context['rid'] = data[0]['reviewer_id_id__u_id']
    context['rphone'] = data[0]['reviewer_id_id__phone']
    context['remail'] = data[0]['reviewer_id_id__email']
    return render(request, 'reviewer_status_check.html', context)

@login_required
def panelmember_status(request,id):
    data = PanelMember.objects.filter(panelmember_id_id__u_id=id).values('proposal_id_id__title','proposal_id_id__proposal_date','proposal_id_id__u_id_id__username','proposal_id_id__u_id_id__phone','proposal_id_id__u_id_id__email',
                                                                   'panelmember_id_id__u_id','panelmember_id_id__username','panelmember_id_id__phone','panelmember_id_id__email',
                                                                   'panel_status','assigned_date','updated_on','panelmember_comments','avg_score')
    print(data)
    context = dict()
    context['data'] = data
    context['panelmember'] = data[0]['panelmember_id_id__username']
    context['rid'] = data[0]['panelmember_id_id__u_id']
    context['rphone'] = data[0]['panelmember_id_id__phone']
    context['remail'] = data[0]['panelmember_id_id__email']
    return render(request, 'panelmember_status_check.html', context)

@login_required
def email_poster(request,id):
    data = Proposal.objects.filter(id=id).values('u_id__username','title','u_id__email')


    title = data[0]['title']
    emails = data[0]['u_id__email']
    applicant_name = data[0]['u_id__username']

    Subject = 'Re: Gentle Reminder for Poster Presentation: '+ title,
    title = title
    emails = emails


    Body = "Dear " + applicant_name + ", \n\n" \
                                      "This is to remind you that your paper has been approved for Poster Presentation for GEARS 2.0. In this regard, we kindly request you to prepare the Poster according to the regulations attached to this mail." "\n\n" \
                                      "You may contact us at 08912840204  or gears_support@gitam.edu  if you have any questions or need any clarifications on them.\n.\n  Best regards, \nG-Venture Funds Team"
    email = EmailMessage(Subject, Body, to=[emails])
    email.attach_file('poster_guide.pdf')
    email.send()
    messages.success(request, "Reminder email sent to scholar")
    return redirect('admin')