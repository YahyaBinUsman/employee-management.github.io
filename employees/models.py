from django.db import models
from django.urls import reverse
import django.contrib.postgres.fields as pgfields 

from django.db import models
from django.urls import reverse

class Employee(models.Model):
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to='employees/', null=True, blank=True)
    face_encoding = models.TextField(null=True, blank=True)  # JSON serialized face encoding
    
    POSITION_CHOICES = [
        ('software_engineer', 'Software Engineer'),
        ('senior_software_engineer', 'Senior Software Engineer'),
        ('devops_engineer', 'DevOps Engineer'),
        ('qa_engineer', 'QA Engineer'),
        ('product_manager', 'Product Manager'),
        ('project_manager', 'Project Manager'),
        ('ui_ux_designer', 'UI/UX Designer'),
        ('graphic_designer', 'Graphic Designer'),
        ('system_architect', 'System Architect'),
        ('cto', 'Chief Technology Officer'),
        ('data_scientist', 'Data Scientist'),
        ('data_analyst', 'Data Analyst'),
        ('security_specialist', 'Security Specialist'),
        ('network_engineer', 'Network Engineer'),
        ('database_administrator', 'Database Administrator'),
        ('hr_manager', 'HR Manager'),
        ('sales_representative', 'Sales Representative'),
        ('customer_support', 'Customer Support'),
    ]

    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        default='software_engineer',
    )

    hourly_rate = models.FloatField(default=15.0)
    overtime_rate = models.FloatField(default=22.5)

    def save(self, *args, **kwargs):
        position_rates = {
            'software_engineer': (40, 60),
            'senior_software_engineer': (50, 75),
            'devops_engineer': (45, 67.5),
            'qa_engineer': (30, 45),
            'product_manager': (55, 82.5),
            'project_manager': (50, 75),
            'ui_ux_designer': (35, 52.5),
            'graphic_designer': (32, 48),
            'system_architect': (60, 90),
            'cto': (70, 105),
            'data_scientist': (55, 82.5),
            'data_analyst': (40, 60),
            'security_specialist': (45, 67.5),
            'network_engineer': (42, 63),
            'database_administrator': (47, 70.5),
            'hr_manager': (35, 52.5),
            'sales_representative': (30, 45),
            'customer_support': (25, 37.5),
        }
        
        if self.position in position_rates:
            self.hourly_rate, self.overtime_rate = position_rates[self.position]
        else:
            self.hourly_rate, self.overtime_rate = (20, 30)  # Default rates

        super(Employee, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    working_hours = models.FloatField(null=True, blank=True)
    normal_salary = models.FloatField(null=True, blank=True)
    overtime_salary = models.FloatField(null=True, blank=True)
    normal_pay = models.FloatField(null=True, blank=True)
    overtime_pay = models.FloatField(null=True, blank=True)
    total_pay = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.entry_time}"

    def get_absolute_url(self):
        return reverse('employee_attendance', args=[str(self.employee.pk)])

    def get_delete_url(self):
        return reverse('delete_attendance', args=[str(self.employee.pk), str(self.pk)])

class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, default=1)
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.employee} - {self.leave_type} - {self.start_date} to {self.end_date}"

from django.db import models

class CustomUser(models.Model):
    bio = models.TextField(blank=True)
    groups = models.ManyToManyField('auth.Group', related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_set', blank=True)

class Page(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
