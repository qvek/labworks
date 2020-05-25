# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.views.generic import ListView
from models import *
from views import student_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm, ModelChoiceField, HiddenInput, IntegerField

class ReportForm(ModelForm):

    labwork_id = IntegerField(widget=HiddenInput())

    def save(self, student, commit=True):
        report = super(ReportForm, self).save(commit=False)
        report.labwork = Labwork.objects.get(id=self.cleaned_data['labwork_id'])
        report.student = student
        if commit:
	    try: report.save()
            except ReportIntegrityError as err:
                report.comment = err.report.comment
                err.report.delete()
                report.update = True
                report.save()
        return report

    class Meta:
        model = Report
        exclude = ('student', 'evaluation', 'labwork', 'comment', 'update')

@student_required
def student_labworks(request, tsg_pk):
    tsg = TeacherSubjectMembership.objects.get(id=tsg_pk)
    labworks_list = LabworkGroupMembership.objects.labworks(request.user.student, tsg.subject, tsg.teacher)

    labworks = labworks_list['labworks']
    score = labworks_list['score']
    labwork_list = []
    context = {}

    if request.method == 'POST' and tsg.isCurrent():
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.user.student)
            return redirect(reverse('student_labworks', kwargs={'tsg_pk':tsg.pk}))
        else:
            context['errors'] = form.errors

    for labwork_el in labworks:
        lsg = labwork_el['lsg']
        labwork = {'labwork':lsg.labwork}
        labwork['report'] = labwork_el['report']
        labwork['deadline'] = lsg.deadline
        if labwork['report']:
            if labwork['report'].date and lsg.deadline:
                labwork['diff'] = labwork['report'].date - lsg.deadline
        if tsg.isCurrent():
            form = ReportForm(initial={'labwork_id':lsg.labwork.id})
            labwork['form'] = form
        labwork_list.append(labwork)

    context['labwork_list'] = labwork_list
    context['score'] = score
    return render(request, "student_labworks.html", context)
