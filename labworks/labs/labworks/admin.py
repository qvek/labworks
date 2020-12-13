from django.contrib import admin
from models import *
from django.contrib.auth import models
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# Register your models here.

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = LabworksUser
        fields = ('email', 'first_name', 'surname', 'last_name', 'is_staff', 'first_enter')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
        
class UserChangeForm(UserCreationForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=False)
    
    
    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        password1 = self.cleaned_data.get("password1")
        if password1 == "":
        	oldpass = LabworksUser.objects.get(pk=user.pk).password
        	user.password = oldpass
        if commit:
            user.save()
        return user

class LabworksUserAdmin(admin.ModelAdmin):
    
    search_fields = ['last_name', 'first_name', 'surname']
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return UserCreationForm
        return  UserChangeForm

class StudentAdmin(admin.ModelAdmin):
    search_fields = ['user__last_name', 'user__first_name', 'user__surname']
    list_display = ('user', 'group')
    list_filter = ('group',)
    
class TeacherAdmin(admin.ModelAdmin):
    search_fields = ['user__last_name', 'user__first_name', 'user__surname']

# Now register the new UserAdmin...
admin.site.register(LabworksUser, LabworksUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(models.Group)

admin.site.register(Group)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject)
admin.site.register(Labwork)
admin.site.register(LabworkGroupMembership)
admin.site.register(Report)
admin.site.register(TeacherSubjectMembership)