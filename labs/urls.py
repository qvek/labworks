from django.conf.urls import patterns, include, url
from django.contrib import admin
from labworks.views import teacher_required, student_required, LabworkCreate, LabworkUpdate, LabworkDelete, CategoryCreate, LabworkList
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'labs.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # urlpatterns = patterns('',) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    url(r'^admin/', include(admin.site.urls)),
    (r'^$', 'labs.labworks.views.index'),
    url(r'archive/$', 'labs.labworks.views.archive', name='archive'),
    url(r'^groups/(?P<subject_id>\d+)$', 'labs.labworks.views.teacher_groups', name='teacher_groups'),
    url(r'^archive_groups/(?P<subject_id>\d+)$', 'labs.labworks.views.teacher_archive_groups', name='teacher_archive_groups'),
    url(r'^labworks/(?P<group_id>\d+)/(?P<subject_id>\d+)$', 'labs.labworks.views.teacher_labworks', name='teacher_labworks'),
    url(r'^subject_summary/(?P<group_id>\d+)/(?P<subject_id>\d+)$', 'labs.labworks.views.teacher_subject_summary', name='teacher_subject_summary'),
    url(r'^excel/(?P<group_id>\d+)/(?P<subject_id>\d+)$', 'labs.labworks.views.teacher_excel', name='teacher_excel'),
    url(r'^labwork/(?P<group_id>\d+)/(?P<labwork_id>\d+)$', 'labs.labworks.views.teacher_labwork', name='teacher_labwork'),
    
    url(r'^labworks/$', LabworkCreate.as_view(), name='teacher_labworks'),
    url(r'^labwork/(?P<pk>\d+)$', LabworkUpdate.as_view(), name='teacher_labwork_update'),
    url(r'^labwork/(?P<pk>\d+)/delete$', LabworkDelete.as_view(), name='teacher_labwork_delete'),
    
    url(r'^lsg_add$', 'labs.labworks.views.teacher_lsg_add', name='teacher_lsg_add'),
    url(r'^lsg_update$', 'labs.labworks.views.teacher_lsg_update', name='teacher_lsg_update'),

    url(r'^set_eval$', 'labs.labworks.views.teacher_set_eval', name='teacher_set_eval'),
    url(r'^set_comment$', 'labs.labworks.views.teacher_set_comment', name='teacher_set_comment'),

    url(r'^labworks/(?P<tsg_pk>\d+)$', 'labs.labworks.student_views.student_labworks', name='student_labworks'),

    url(r'^categories/$', CategoryCreate.as_view(), name='teacher_categories'),
    url(r'^category_labworks/([\w-]+)/$', LabworkList.as_view(), name='teacher_category_labworks'),

    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', {'template_name': 'password_change.html'}, name='password_change'),
    url(r'^password_change_done/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'password_change_done.html'}, name='password_change_done'),
     
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', {'template_name': 'password_reset.html'}, name='password_reset'),
    url(r'^password_reset_done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'password_reset_done.html'}, name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name': 'password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete',  {'template_name': 'password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^plans/', {'temlate_name': 'plans.html'}, name='plans')
)
