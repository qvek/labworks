# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.forms.models import inlineformset_factory
import django.forms as forms
from django.core.mail import send_mail
from labs import settings
from models import *
import xlsxwriter
import os
import mimetypes
from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
import urllib2

# Create your views here.

def user_required(function, user):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, user):
            return redirect(settings.LOGIN_URL)
        try:
            return function(request, *args, **kwargs)
        except NoPermissionError as err:
            return HttpResponse(err)

    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    return wrapper

def teacher_required(function):
    return user_required(function, 'teacher')

def student_required(function):
    return user_required(function, 'student')

@login_required
def index(request):
    if request.user.is_student():
        subjects = request.user.student.subjects()
        return render(request, "student_index.html", {'subjects':subjects})
    elif request.user.is_teacher(): # список групп преподавателя
        subjects = request.user.teacher.subjects()
        return render(request, "teacher_index.html", {'subjects':subjects})
    else: return HttpResponse("Who are you?")

@login_required
def archive(request):
    """ Архив: список прошедших дисциплин """
    if request.user.is_student():
        subjects = request.user.student.archiveSubjects()
        return render(request, "student_index.html", {'subjects':subjects})
    elif request.user.is_teacher(): # список групп преподавателя
        subjects = request.user.teacher.archiveSubjects()
        return render(request, "teacher_index.html", {'subjects':subjects, 'archive':True})
    else: return HttpResponse("Who are you?")

@teacher_required
def teacher_groups(request, subject_id):
    """ Список групп """
    subject = Subject.objects.get(id=subject_id)
    groups = request.user.teacher.groups(subject)
    return render(request, "teacher_group.html", {'subject':subject, 'groups':groups})

@teacher_required
def teacher_archive_groups(request, subject_id):
    """ Архив: Список групп """
    subject = Subject.objects.get(id=subject_id)
    groups = request.user.teacher.archiveGroups(subject)
    return render(request, "teacher_group.html", {'subject':subject, 'groups':groups})

@teacher_required
def teacher_labworks(request, group_id, subject_id):
    """ список лабораторных """
    group = Group.objects.get(id=group_id)
    subject = Subject.objects.get(id=subject_id)
    lsg_list = LabworkGroupMembership.objects.labworks_group(teacher=request.user.teacher, group=group, subject=subject)
    return render(request, "teacher_subject.html", {'lsg_list':lsg_list, 'group':group, 'subject':subject})

@teacher_required
def teacher_labwork(request, group_id, labwork_id):
    """ отчетность по лабораторной """
    group = Group.objects.get(id=group_id)
    labwork = Labwork.objects.get(id=labwork_id)

    if labwork.teacher != request.user.teacher: # а эта лабораторная принадлежит преподу?
        raise NoPermissionError(unicode(request.user.teacher)+u" не ведет лабораторную "+unicode(labwork))

    students = labwork.reports(group)
    for student in students:
        if 'report' in student.keys():
            student['form'] = forms.Select(choices=(
             ('0', 'Нет оценки'),
	     ('1', '1'),
	     ('2', '2'),
	     ('3', '3'),
	     ('4', '4'),
	     ('5', '5')), attrs={'data-id':student['report'].id}).render('evaluation', student['report'].evaluation)

            lsg = LabworkGroupMembership.objects.filter(group=group, labwork=labwork)[0]
            if student['report'].date and lsg.deadline:
                student['diff'] = student['report'].date - lsg.deadline

    return render(request, "teacher_labwork.html", {'students':students, 'group':group, 'labwork':labwork})

@teacher_required
def teacher_subject_summary(request, group_id, subject_id):
    group = Group.objects.get(id=group_id)
    subject = Subject.objects.get(id=subject_id)
    lsg_list = LabworkGroupMembership.objects.labworks_group(teacher=request.user.teacher, group=group, subject=subject, no_check=True)

    reports = LabworkGroupMembership.objects.labworks_reports(group, subject, request.user.teacher)
    students = []
    for student_reports in reports:
        student_set = {'student':student_reports['student'], 'reports':[]}
        for lsg in student_reports['labworks']['labworks']:
            if lsg['lsg'].labwork.no_check: continue
            report = lsg['report']
            if report:
                form = forms.Select(choices=(
                 ('0', 'н/а'),
	             ('1', '1'),
	             ('2', '2'),
	             ('3', '3'),
	             ('4', '4'),
                 ('5', '5')), attrs={'data-id':report.id}).render('evaluation', report.evaluation)
                student_set['reports'].append({'report':report, 'form':form})
            else:
                student_set['reports'].append({'report':report})
        student_set['score'] = student_reports['labworks']['score']
        students.append(student_set)
    return render(request, "teacher_subject_summary.html", {'students':students, 'lsg_set':lsg_list, 'group_id':group_id, 'subject_id':subject_id})

@teacher_required
def teacher_excel(request, group_id, subject_id):
    group = Group.objects.get(id=group_id)
    subject = Subject.objects.get(id=subject_id)
    #lsg_list = LabworkGroupMembership.objects.labworks_group(teacher=request.user.teacher, group=group, subject=subject)

    filename = 'excel_'+group.name+'_'+subject.name+'.xlsx'
    path = os.path.abspath(settings.EXCEL_ROOT)+'/'+filename
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet()

    font_size = 16

    font = workbook.add_format({'font_size':font_size})
    bold = workbook.add_format({'bold': True, 'font_size':font_size})
    bold_center = workbook.add_format({'bold':True, 'align':'center', 'font_size':font_size})
    group_name = workbook.add_format({'bold':True, 'align':'center', 'font_size':24})
    center = workbook.add_format({'align':'center', 'font_size':font_size})
    red = workbook.add_format({'align':'center', 'font_size':font_size, 'bg_color':'#fc2847'})

    worksheet.write('A2', u'Студент', bold)
    worksheet.set_column(0, 0, 30)

    worksheet.write('B2', u'Средний балл', bold_center)
    worksheet.set_column(1, 1, 17)

    row = 2

    reports = LabworkGroupMembership.objects.labworks_reports(group, subject, request.user.teacher)
    for student_reports in reports:
        worksheet.write(row, 0, unicode(student_reports['student']), font)
        score = student_reports['labworks']['score']
        if score < 3.0: worksheet.write(row, 1, score, red)
        else: worksheet.write(row, 1, score, center)

        for i, lsg in enumerate(student_reports['labworks']['labworks']):
            if lsg['lsg'].labwork.code: labwork_label = unicode(lsg['lsg'].labwork.code)
            else: labwork_label = unicode(lsg['lsg'].labwork.name)
            worksheet.write(1, i+2, labwork_label, bold_center)
            report = lsg['report']
            if report:
                if report.evaluation > 2: worksheet.write(row, i+2, report.evaluation, center)
                else: worksheet.write(row, i+2, report.evaluation, red)
            else: worksheet.write(row, i+2, '-', red)

        row += 1

    worksheet.merge_range(0, 0, 0, len(student_reports['labworks']['labworks'])+2, group.name, group_name) #Указываем имя группы

    workbook.close()

    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(path), chunk_size), content_type=mimetypes.guess_type(path)[0])
    response['Content-Length'] = os.path.getsize(path)
    url = urllib2.quote(unicode(filename).encode('utf8'))
    response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % url
    return response

@teacher_required
@require_POST
def teacher_set_eval(request):
    report = Report.objects.get(id=request.POST['report_id'])
    if report.labwork.teacher != request.user.teacher: raise NoPermissionError('This is not teacher')
    report.evaluation = request.POST['evaluation']
    report.save()
    return HttpResponse(report.evaluation)

@teacher_required
@require_POST
def teacher_set_comment(request):
    report = Report.objects.get(id=request.POST['report_id'])
    if report.labwork.teacher != request.user.teacher: raise NoPermissionError('This is not teacher')
    report.comment = request.POST['comment']
    report.update = False
    report.save()
    if report.comment != '':
        send_mail(u"Комментарий по "+report.labwork.name, report.comment, report.labwork.teacher.user.email, [report.student.user.email], fail_silently=False)
    return HttpResponse('ok')

class LSGForm(forms.ModelForm):

    labwork = forms.ModelChoiceField(queryset=Labwork.objects.filter(), widget=forms.HiddenInput)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.filter(), label='Группы', widget=forms.SelectMultiple(attrs={'class': 'groups'}))

    def save(self, commit=True):
        copy = dict(self.cleaned_data)
        copy.pop('groups', None)

        for group in self.cleaned_data['groups']:
            copy['group'] = group
            lsg = LabworkGroupMembership(**copy)
            if commit: lsg.save()

    class Meta:
        model = LabworkGroupMembership
        fields = ['groups', 'labwork', 'subject', 'status', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'class': 'deadline'}),
        }

@teacher_required
@require_POST
def teacher_lsg_add(request):
    """ добавляет L-S-G """
    form = LSGForm(request.POST)
    labwork_id = request.POST['labwork']
    if form.is_valid():
        form.save()
    else:
        request.session['data'] = form.cleaned_data
    return redirect(reverse('teacher_labwork_update', args=[labwork_id]))

@teacher_required
@require_POST
def teacher_lsg_update(request):
    """ изменяет L-S-G """
    labwork_id = request.POST['labwork']
    labwork = Labwork.objects.get(id=labwork_id)
    LSGFormSet = inlineformset_factory(Labwork, LabworkGroupMembership, max_num=0, fields=('group', 'subject', 'status', 'deadline'))
    lsg_formset = LSGFormSet(request.POST, instance=labwork)
    if lsg_formset.is_valid():
        lsg_formset.save()
    else:
        request.session['set_data'] = request.POST
    return redirect(reverse('teacher_labwork_update', args=[labwork_id]))

class LabworkView(FormView):

    model = Labwork
    fields = ['name', 'code', 'no_check', 'file', 'parent', 'category']

    @method_decorator(teacher_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LabworkView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher
        return super(LabworkView, self).form_valid(form)

    def get_object(self, queryset=None):
        object = super(LabworkView, self).get_object(queryset)
        if object.teacher != self.request.user.teacher:
            raise NoPermissionError(unicode(self.request.user.teacher)+u" не ведет лабораторную "+unicode(object))
        return object

    def get_form(self, form_class=None):
        """ пришивает работы преподователя """
    	if form_class is None:
            form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        form.fields['parent'].queryset = self.get_parent_queryset()
        form.fields['category'].queryset = self.get_category_queryset()
        return form

    def get_parent_queryset(self):
        """ пришивает все работы преподавателя (для страницы создания) """
        return self.request.user.teacher.labwork_set.all()

    def get_category_queryset(self):
        """ пришивает все категории преподавателя (для страницы создания) """
        return self.request.user.teacher.category_set.all()

class LabworkCreate(LabworkView, CreateView):

    template_name = "teacher_labworks.html"

    def get_context_data(self, **kwargs):
        context = super(LabworkCreate, self).get_context_data(**kwargs)
        context['labworks'] = self.request.user.teacher.labwork_set.filter(category=None)
        context['categories'] = Category.objects.filter(teacher=self.request.user.teacher)
        return context

class LabworkUpdate(LabworkView, UpdateView):

    template_name = "teacher_labwork_update.html"

    def get_parent_queryset(self):
        """ пришивает все работы кроме текущей (для страницы обновления) """
        labwork = self.get_object()
        return self.request.user.teacher.labwork_set.filter(category=labwork.category).exclude(id=labwork.id)

    def get_context_data(self, **kwargs):
        context = super(LabworkUpdate, self).get_context_data(**kwargs)

        form = LSGForm(self.request.session.get('data', None), initial={'labwork': self.get_object().pk})

        groups = self.request.user.teacher.groups() #группы преподавателя T-S-G
        groups_pk_set = [group.pk for group in groups]
        groups = Group.objects.filter(pk__in=groups_pk_set) #группы преподавателя L-S-G
        form.fields['groups'].queryset = groups

        subjects = self.request.user.teacher.subjects() #дисциплины преподаватея T-S-G
        subjects_pk_set =[subject.pk for subject in subjects]
        subjects = Subject.objects.filter(pk__in=subjects_pk_set) #дисциплины преподаватея L-S-G
        form.fields['subject'].queryset = subjects

        LSGFormSet = inlineformset_factory(Labwork, LabworkGroupMembership, max_num=0, fields=('group', 'subject', 'status', 'deadline')) #Набор форм
        lsg_formset = LSGFormSet(self.request.session.get('set_data', None), instance=self.get_object(), queryset=LabworkGroupMembership.objects.filter(group__in=groups, subject__in=subjects))

        for lsg in lsg_formset: #подкручиваем группы и дисциплины преподавателя
            lsg.fields['group'].queryset = groups
            lsg.fields['subject'].queryset = subjects

        context['lsg_form'] = form
        context['lsg_formset'] = lsg_formset

        if 'data' in self.request.session.keys():
            del self.request.session['data']
        if 'set_data' in self.request.session.keys():
            del self.request.session['set_data']
        return context

class LabworkDelete(LabworkView, DeleteView):

    template_name = "teacher_labwork_delete.html"
    success_url = reverse_lazy('teacher_labworks')

class CategoryCreate(CreateView):

    model = Category
    fields = ['name']
    template_name = "teacher_category_create.html"

    @method_decorator(teacher_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CategoryCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher
        return super(CategoryCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CategoryCreate, self).get_context_data(**kwargs)
        context['categories'] = self.request.user.teacher.category_set.all()
        return context

class LabworkList(ListView):

    template_name = "teacher_category_labworks.html"
    context_object_name = "labworks"

    @method_decorator(teacher_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LabworkList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        category = Category.objects.get(pk=self.args[0])
        return Labwork.objects.filter(category=category)