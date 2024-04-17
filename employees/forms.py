

from django import forms
from .models import Employee, Attendance, Leave



class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'first_name', 'last_name', 'email', 'phone', 'position', 'image']
        widgets = {
            'position': forms.Select(choices=Employee.POSITION_CHOICES),
        }


# Form for capturing entry time in the Attendance model.
class EntryForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = []
# Form for capturing exit time in the Attendance model.
class ExitForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['exit_time']

#  Form for capturing attendance information.
class AttendanceForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())
    class Meta:
        model = Attendance
        fields = ['employee']

# Form for capturing leave request information.
class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']

    # Use ModelChoiceField to create a dropdown list for employees
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), empty_label=None)
    widgets = {
            'employee': forms.Select(attrs={'class': 'employee-field'}),
        }

# forms.py
from django import forms

class ImageForm(forms.ModelForm):
    class Meta:
        fields = ['employee']


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# SignUpForm
class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

