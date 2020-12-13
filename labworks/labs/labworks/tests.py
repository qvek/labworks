# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from models import *
import views

# Create your tests here.

class SimpleTest(TestCase):
    def setUp(self):
    
        self.user_stogov = LabworksUser.objects.create_user(email = 'e.a.stogov@mpt.ru', password = '1', first_name='Евгений', surname='Александрович', last_name='Стогов')
        self.stogov = Teacher.objects.create(user=self.user_stogov)
        self.stogov.save()
        
        self.user_silaev = LabworksUser.objects.create_user(email = 'n.o.silaev@mpt.ru', password = '1', first_name='Никита', surname='Олегович', last_name='Силаев')
        self.silaev = Teacher.objects.create(user=self.user_silaev)
        self.silaev.save()
        
        self.ks111 = Group.objects.create(name='КС-1-11')
        self.ks111.save()
        
        self.user_dima = LabworksUser.objects.create_user(email = 'st_d.s.harchenko@mpt.ru', password = '1', first_name='Дмитрий', surname='Сергеевич', last_name='Харченко')
        self.dima = Student.objects.create(user=self.user_dima, group=self.ks111)
        
        self.ks112 = Group.objects.create(name='КС-1-12')
        self.ks112.save()
        
        self.subject_stogov = Subject.objects.create(code='code', name='Сетевые языки')
        self.subject_stogov.save()
        
        self.subject_silaev = Subject.objects.create(code='code 2', name='Компьютерные сети')
        self.subject_silaev.save()
        
        self.stogov_tsg = TeacherSubjectMembership(teacher=self.stogov, subject=self.subject_stogov, group=self.ks111)
        self.stogov_tsg.save()
        
        self.silaev_tsg = TeacherSubjectMembership(teacher=self.silaev, subject=self.subject_silaev, group=self.ks112)
        self.silaev_tsg.save()
        
        self.labwork = Labwork.objects.create(name='name', file='file', teacher=self.stogov)
        self.labwork.save()
        
        self.lsg = LabworkGroupMembership(labwork=self.labwork, group=self.ks111, subject=self.subject_stogov, status=True)
        self.lsg.save()
        
        self.report = Report(file='', student=self.dima, labwork=self.labwork)
        self.report.save()
        
        self.c = Client()
        self.c.login(username='e.a.stogov@mpt.ru', password='1')

    #def test_details(self):
    #    response = self.c.get('')
    #    self.assertEqual(response.context['groups'], [self.ks111])
        
    #def test_teacher_group(self):
    #    response = self.c.get(reverse('teacher_group', args=[self.ks111.pk,]))
    #    self.assertEqual(response.context['subjects'], [self.subject_stogov])
        
    def test_set_eval(self):
        response = self.c.post(reverse('teacher_set_eval'), {'evaluation':5, 'report_id':self.report.id})
        self.assertEqual(response.content, '5')