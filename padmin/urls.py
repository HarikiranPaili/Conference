from .views import admin_reupload, addreviewer, addpanelmember,selected_campus,selected_inst,\
    selected_dept,add_new_reviewer,add_new_panelmember,add_external_panelmember,send_bulk_email,\
    results,panel_upload, add_scholars,selected_results,scholar_view,admin_reviewer_document,\
    change_reviewer_document,reviewer_status,panelmember_status,email_poster
from django.urls import path, include

urlpatterns = [

    path('admin_reupload',admin_reupload, name='admin_reupload'),
    path('addreviewer',addreviewer, name='addreviewer'),
    path('addpanelmember',addpanelmember, name='addpanelmember'),
    path('add_external_panelmember',add_external_panelmember, name='add_external_panelmember'),
    path('selected_campus',selected_campus, name='selected_campus'),
    path('selected_results',selected_results, name='selected_results'),
    path('selected_inst',selected_inst, name='selected_inst'),
    path('selected_dept',selected_dept, name='selected_dept'),
    path('add_new_reviewer',add_new_reviewer, name='add_new_reviewer'),
    path('email_poster/<str:id>/',email_poster, name='email_poster'),
    path('send_bulk_email/<str:Empid>/<str:role>/',send_bulk_email, name='send_bulk_email'),
    path('add_new_panelmember',add_new_panelmember, name='add_new_panelmember'),
    path('scholar_view/<int:id>/',scholar_view, name='scholar_view'),
    path('panel_upload',panel_upload, name='panel_upload'),
    path('add_scholars',add_scholars, name='add_scholars'),
    path('results',results, name='results'),
    path('admin_reviewer_document/<int:id>/', admin_reviewer_document, name='admin_reviewer_document'),
    path('change_reviewer_document', change_reviewer_document, name='change_reviewer_document'),
    path('reviewer_status/<int:id>/', reviewer_status, name='reviewer_status'),
    path('panelmember_status/<str:id>/', panelmember_status, name='panelmember_status'),

]
