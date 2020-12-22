# -*- coding: utf-8 -*-

from django.db import models, IntegrityError
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.core.urlresolvers import reverse, reverse_lazy
import datetime

class NoPermissionError(Exception): pass

class TSMQuerySet(models.query.QuerySet):
    """ для удаления связи T-S-G """

    def delete(self):
        """ делаем не сразу запрос, а удалеям по очереди каждый объект """
        del_query = self._clone()
        for obj in del_query:
            obj.delete()

class TSManager(models.Manager):
    """ для того чтобы пришить TSMQuerySet к TeacherSubjectMembership """
    def get_queryset(self):
        return TSMQuerySet(self.model, using=self._db)

# Create your models here.

class LabworksUserManager(BaseUserManager):

    def create_user(self, **kwargs):
        user = LabworksUser(**kwargs)
        user.set_password(kwargs['password'])
        user.save()
        return user
        
    def create_superuser(self, email, password):
        user = LabworksUser(email=email)
        user.is_staff = True
        user.set_password(password)
        user.save()
        return user

class LabworksUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    first_enter = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    
    objects = LabworksUserManager()
    
    def get_short_name(self):
        # The user is identified by their email address
        return self.email
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
        
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
        
    def is_student(self):
        return hasattr(self, 'student')
        
    def is_teacher(self):
        return hasattr(self, 'teacher')
        
    def __unicode__(self):
        return self.first_name[0:1]+'. '+self.surname[0:1]+'. '+self.last_name
        
    class Meta:
        ordering = ('last_name', 'first_name', 'surname')

class Group(models.Model):
    name = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.name
        
    def __int__(self):
        return self.id
        
    class Meta:
        get_latest_by = 'name'
        ordering = ('name',)

class Name:

    def __unicode__(self):
        return u'{0[0]}.{1[0]}. {2}'.format(self.user.first_name, self.user.surname, self.user.last_name)

class Student(models.Model, Name):
    user = models.OneToOneField(LabworksUser)
    group = models.ForeignKey(Group, verbose_name="Группа")
    
    def subjects(self):
        """ список дисциплин для студента """
        return TeacherSubjectMembership.objects.filter(group=self.group, date_start__lte=datetime.date.today(), date_end__gte=datetime.date.today())

    def archiveSubjects(self):
        """ Архив: список прошедших дисциплин студента """
        return TeacherSubjectMembership.objects.filter(group=self.group).exclude(date_start__lte=datetime.date.today(), date_end__gte=datetime.date.today())

    def reports(self):
        return Report.objects.filter(student=self)

    class Meta:
        ordering = ('user',)
  
class Teacher(models.Model, Name):
    user = models.OneToOneField(LabworksUser)
    
    def getItems(self, param, params={}, archive=False):
        """ обобщающий для методов groups и subjects """
        params['teacher'] = self
        dates = {'date_start__lte':datetime.date.today(), 'date_end__gte':datetime.date.today()} # период для выбора дисциплин
        tsg_list = TeacherSubjectMembership.objects.filter(**params)
        if archive: tsg_list = tsg_list.exclude(**dates) # Архив: список прошедших дисциплин, поэтому исключаем только текущие дисциплины
        else: tsg_list = tsg_list.filter(**dates) # Иначе выбираем только текущие дисциплины
        tsg_list = tsg_list.order_by(param)
        items = []
        for tsg in tsg_list:
            if getattr(tsg, param) not in items:
                items.append(getattr(tsg, param))
        return items
    
    def groups(self, subject=None):
        """ возвращает группы преподавателя """
        if subject:
            return self.getItems('group', params={'subject':subject})
        return self.getItems('group')

    def archiveGroups(self, subject=None):
        """ Архив: возвращает список прошедших групп преподавателя. """
        if subject:
            return self.getItems('group', params={'subject':subject}, archive=True)
        return self.getItems('group', archive=True)
        
    def subjects(self, group=None):
        """ возвращает список дисциплин преподавателя. """
        if group:
            return self.getItems('subject', params={'group':group})
        return self.getItems('subject')

    def archiveSubjects(self, group=None):
        """ Архив: возвращает список прошедших дисциплин преподавателя. """
        if group:
            return self.getItems('subject', params={'group':group}, archive=True)
        return self.getItems('subject', archive=True)
    
    class Meta:
        ordering = ('user',)

class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.code+" "+self.name
        
    def __int__(self):
        return self.id
        
    class Meta:
        ordering = ('code', 'name')

class TeacherSubjectMembership(models.Model):
    """ T-S-G """
    teacher = models.ForeignKey(Teacher)
    subject = models.ForeignKey(Subject)
    group = models.ForeignKey(Group)
    date_start = models.DateField(null=True, verbose_name='Дата начала')
    date_end = models.DateField(null=True, verbose_name='Дата окончания')
    
    objects = TSManager()
    
    def __unicode__(self):
        return unicode(self.group)+" "+unicode(self.subject)+" "+unicode(self.teacher)
            
    def delete(self, using=None):
        """ при удалении связи T-S-G удаляем и все дочерние связи L-S-G """
        LabworkGroupMembership.objects.filter(labwork__teacher=self.teacher, group=self.group, subject=self.subject).delete()
        super(TeacherSubjectMembership, self).delete()

    def isCurrent(self):
        """ проверка является ли T-S-G текущей """
        if self.date_start is None or self.date_end is None: return False
        return self.date_start <= datetime.date.today() <= self.date_end

    class Meta:
        unique_together = ('teacher', 'subject', 'group')

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    teacher = models.ForeignKey(Teacher)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('teacher_categories')

class Labwork(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    code = models.CharField(max_length=10, null=True, blank=True, verbose_name='Код')
    no_check = models.BooleanField(default=False, verbose_name='Не оценивать')
    file = models.FileField(verbose_name='Файл')
    teacher = models.ForeignKey(Teacher)
    groups = models.ManyToManyField(Group, through='LabworkGroupMembership')
    parent = models.ForeignKey('self', null=True, blank=True, verbose_name='Предыдущая работа')
    category = models.ForeignKey(Category, null=True, blank=True, verbose_name='Категория')
    
    def __unicode__(self):
        return self.name
        
    def __int__(self):
        return self.id
        
    def save(self, *args, **kwargs):
        if self.parent and self.teacher != self.parent.teacher: raise NoPermissionError(unicode(self.teacher)+u" не владеет работой "+unicode(self.parent))
        super(Labwork, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('teacher_labwork_update', kwargs={'pk': self.pk})
    
    def reports(self, group):
        """ список студентов с отчетами """
        tsg_set = TeacherSubjectMembership.objects.filter(teacher=self.teacher, group=group)
        if tsg_set.count() == 0: # препод не ведет у этой группы
            raise NoPermissionError(unicode(self.teacher)+u" не ведет у "+unicode(group))
            
        students = []
        for student in group.student_set.order_by('user__last_name'):
            sr = {'student':student}
            try:
                sr['report'] = student.report_set.get(labwork=self)
            except Report.DoesNotExist: pass
            students.append(sr)
        return students

    def report(self, student):
        try:
            return Report.objects.get(student=student, labwork=self)
        except Report.DoesNotExist:
            return None

class LSGManager(models.Manager):

    def _labworks(self, group, subject, teacher=None, status=True):
        """ возвращает лабораторные работы. САМЫЙ ЯДЕРНЫЙ МЕТОД """
        params = {'subject':subject, 'group':group, 'status':status}
        if teacher:
            params['labwork__teacher'] = teacher
        return self.filter(**params)

    def labworks(self, student, subject, teacher, parent_f=True):
        """ возвращает список лабораторных работ для студента. Выполняет подсчет среднего балла """
        lsg_set = self._labworks(student.group, subject, teacher)

        score = 0.0
        nocheck = 0

        labworks = [] #лабы, которые будут показаны студенту
        for lsg in lsg_set:
            labwork = {'lsg':None, 'report':None}

            if lsg.labwork.no_check: nocheck += 1

            if lsg.labwork.parent and parent_f:
                parent = lsg.labwork.parent.report(student)
                if parent and parent.evaluation > 0: labwork['lsg'] = lsg
            else: labwork['lsg'] = lsg

            report = lsg.labwork.report(student)
            status = lsg.status

            if report and status:
                score += report.evaluation
                labwork['report'] = report

            if labwork['lsg']: labworks.append(labwork)

        if len(labworks)-nocheck > 0:
            score /= len(labworks)-nocheck
            score = round(score, 1)

        return {'labworks': labworks, 'score': score}

    def labworks_group(self, group, subject, teacher=None, status=True, no_check=False):
        """ возвращает список лабораторных работ. Используется для преподов. """
        labworks = self._labworks(group, subject, teacher, status)
        if no_check: labworks = labworks.exclude(labwork__no_check=True) #убирает работы, которые не надо проверять
        return labworks

    def labworks_reports(self, group, subject, teacher):
        """ для создания сводной таблицы. Обращется к LSG и Report """

        students = []
        for student in group.student_set.all():
            students.append({'student':student, 'labworks':self.labworks(student, subject, teacher, parent_f=False)})

        return students

class LabworkGroupMembership(models.Model):
    labwork = models.ForeignKey(Labwork)
    group = models.ForeignKey(Group, verbose_name="Группа")
    
    subject = models.ForeignKey(Subject, verbose_name="Дисциплина") #default=None
    status = models.BooleanField(default=False, verbose_name="Открыта")
    
    deadline = models.DateField(null=True, blank=True, verbose_name="Срок сдачи")
    
    objects = LSGManager()
    
    def __unicode__(self):
        return unicode(self.labwork)+" "+unicode(self.group)+" "+unicode(self.subject)
        
    def save(self, *args, **kwargs):
        """ для того чтобы задать лабораторную группе должна быть связь T-S-G """
        try:
            TeacherSubjectMembership.objects.get(teacher=self.labwork.teacher, subject=self.subject, group=self.group)
        except TeacherSubjectMembership.DoesNotExist:
            raise NoPermissionError(unicode(self.labwork.teacher)+u" не ведет "+unicode(self.subject)+u" у "+unicode(self.group))
        else:
            super(LabworkGroupMembership, self).save(*args, **kwargs)

class ReportIntegrityError(IntegrityError):
    
    def __init__(self, cause, report_id):
        super(ReportIntegrityError, self).__init__(cause)
        self.report = Report.objects.get(id=report_id)

class Report(models.Model):
    file = models.FileField(verbose_name='Файл')
    student = models.ForeignKey(Student)
    labwork = models.ForeignKey(Labwork)
    evaluation = models.IntegerField(default=0)
    comment = models.TextField(blank=True, default='')
    date = models.DateField(auto_now_add=True, null=True)
    update = models.NullBooleanField(null=True, default=False)
    
    def save(self, *args, **kwargs):
        """ у студента на лабораторную по одному отчету """
        try:
            report = Report.objects.get(student=self.student, labwork=self.labwork)
        except Report.DoesNotExist: #создание отчета
            super(Report, self).save()
        else:
            if report.id == self.id: #обновление отчета
                super(Report, self).save()
            else: #защита от дублирования
                raise ReportIntegrityError("Duplicate entry "+str(report.id), report.id)
