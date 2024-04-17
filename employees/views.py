
import binascii
import datetime
import pickle
import base64
import cv2
from io import BytesIO
from PIL import Image
import numpy as np
import face_recognition
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import (
    AttendanceForm,
    LeaveForm,
    EmployeeForm,
    ImageForm,
    SignUpForm
)
from .models import Attendance, Employee, Leave

from django.views.decorators.http import require_POST
import datetime
from datetime import timedelta

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

# Lists employees, supports search functionality, and pagination.
@login_required
def employee_list(request):
    query = request.GET.get('q')
    
    if query:
        employees = Employee.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        )
    else:
        employees = Employee.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(employees, 10)

    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        employees = paginator.page(1)
    except EmptyPage:
        employees = paginator.page(paginator.num_pages)

    selected_employee = None

    # Check if a specific employee is selected
    employee_pk = request.GET.get('employee_pk')
    if employee_pk:
        try:
            selected_employee = Employee.objects.get(pk=employee_pk)
        except Employee.DoesNotExist:
            raise Http404("Employee does not exist")

    return render(request, 'employee_list.html', {'employees': employees, 'query': query, 'selected_employee': selected_employee})

# Displays details of a specific employee.
@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employee_detail.html', {'employee': employee})



@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()

            # Handle the image separately
            image_file = request.FILES.get('image')
            if image_file:
                file_name = f"{employee.id}_{image_file.name}"
                file_path = default_storage.save(file_name, ContentFile(image_file.read()))
                employee.image = file_path
                employee.save()

            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee_edit.html', {'form': form})

# Handles the deletion of an existing employee.
@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    
    return render(request, 'employee_delete.html', {'employee': employee})

#   Lists all employees.
@login_required
def all_employees(request):
    employees = Employee.objects.all()
    return render(request, 'all_employees.html', {'employees': employees})

# Deletes an attendance record.
@login_required
def delete_attendance(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        attendance.delete()
        return redirect('employee_attendance')

    return render(request, 'delete_attendance.html', {'attendance': attendance})

# Updates the exit time for an attendance record.
@login_required
def update_exit_time(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        attendance.exit_time = timezone.now()
        attendance.save()

    return redirect('employee_attendance')  # Redirect back to the attendance page

# Calculates salary based on attendance records.
@login_required
def calculate_salary(request):
    attendances = Attendance.objects.select_related('employee').all()

    for attendance in attendances:
        if attendance.entry_time and attendance.exit_time:
            working_hours = (attendance.exit_time - attendance.entry_time).seconds / 3600
            normal_hours = min(working_hours, 8)
            overtime_hours = max(working_hours - 8, 0)

            normal_pay = normal_hours * attendance.employee.hourly_rate
            overtime_pay = overtime_hours * attendance.employee.overtime_rate
            total_pay = normal_pay + overtime_pay

            # Update the attendance object with the calculated values
            attendance.working_hours = working_hours
            attendance.normal_hours = normal_hours
            attendance.overtime_hours = overtime_hours
            attendance.normal_pay = normal_pay
            attendance.overtime_pay = overtime_pay
            attendance.total_pay = total_pay
            attendance.save()  # Don't forget to save the updates

    context = {'attendances': attendances}
    return render(request, 'calculate_salary.html', context)

# Helper function to calculate hourly salary.
@login_required
def calculate_hourly_salary(working_hours):
    # Constants
    standard_working_hours = 8
    hourly_rate = 8
    overtime_rate = 12

    # Calculate overtime hours
    overtime_hours = max(working_hours - standard_working_hours, 0)

    # Calculate salary
    salary = (standard_working_hours * hourly_rate) + (overtime_hours * overtime_rate)

    return salary


# Handles the submission of leave requests.
@login_required
def leave_request(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee_name = form.cleaned_data['employee'].first_name  # Assuming 'first_name' is the field you want
            leave.save()
            return redirect('leave_requests')
    else:
        form = LeaveForm()

    return render(request, 'leave_request.html', {'form': form})


# Lists all leave requests.
@login_required
def leave_requests(request):
    leave_requests = Leave.objects.all()
    context = {'leave_requests': leave_requests}
    return render(request, 'leave_requests.html', context)
@login_required
def home_page(request):
    return render(request, 'home.html')

def is_admin(user):
    return user.is_authenticated and user.is_staff
@login_required
@user_passes_test(is_admin)
def process_leave_status(request, leave_id, status):
    leave = Leave.objects.get(pk=leave_id)

    if request.method == 'POST':
        leave.status = status
        leave.save()
        return redirect('leave_requests')

    return render(request, 'leave_requests.html', {'leave_requests': Leave.objects.all()})

def get_employee_data(name):
    try:
        employee = Employee.objects.get(name=name)
        return employee
    except Employee.DoesNotExist:
        return None
    


import face_recognition
from django.http import JsonResponse
from .forms import AttendanceForm, EmployeeForm
from .models import Employee, Attendance
from django.shortcuts import render, redirect
from django.utils import timezone
import json

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import face_recognition
import numpy as np
from PIL import Image
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EmployeeForm
from .models import Employee
import face_recognition
import numpy as np
from PIL import Image
import json
import logging

@login_required
def employee_new(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            
            if 'image' in request.FILES:
                image = request.FILES['image']
                try:
                    pil_image = Image.open(image).convert("RGB")
                    np_image = np.array(pil_image)
                    face_encodings = face_recognition.face_encodings(np_image)
                    
                    if face_encodings:
                        employee.face_encoding = json.dumps(face_encodings[0].tolist())
                        employee.save()
                        return redirect('employee_detail', pk=employee.pk)
                    else:
                        # Face not detected
                        logging.error("No faces were detected in the uploaded image.")
                        form.add_error('image', "No faces detected in the image. Please upload a clear frontal face image.")
                except Exception as e:
                    logging.error(f"Error processing image: {e}")
                    form.add_error('image', "Error processing the image.")
            else:
                form.add_error('image', "Please upload an image.")
        else:
            logging.error("Form is not valid")
            logging.error(form.errors)
    else:
        form = EmployeeForm()
    
    return render(request, 'employee_edit.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employee, Attendance
from .forms import AttendanceForm
from django.utils import timezone
# Assuming you have a form named AttendanceForm in your forms.py

from django.contrib import messages
from django.utils import timezone
@login_required
def employee_attendance(request):
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data['employee']
            employee = get_object_or_404(Employee, pk=employee_id)
            Attendance.objects.create(employee=employee, entry_time=timezone.now())
            messages.success(request, "Attendance marked successfully.")
            return redirect('employee_attendance')
        else:
            messages.error(request, "Invalid form submission.")
            return redirect('employee_attendance')
    else:
        form = AttendanceForm()
        employees = Employee.objects.all()
        attendances = Attendance.objects.order_by('-entry_time')
        return render(request, 'employee_attendance.html', {
            'form': form,
            'employees': employees,
            'attendances': attendances,
        })
from django.utils import timezone
from django.http import JsonResponse
from .models import Employee, Attendance

@login_required
def check_recent_attendance(request, employee_id):
    last_attendance = Attendance.objects.filter(employee_id=employee_id).order_by('-entry_time').first()
    if last_attendance and (timezone.now() - last_attendance.entry_time).total_seconds() / 3600 < 12:
        return JsonResponse({'status': 'error', 'message': 'Cannot mark attendance more than once within 12 hours.'})
    return JsonResponse({'status': 'ok'})

@login_required
def add_entry_time(request, employee_id):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, pk=employee_id)
        Attendance.objects.create(employee=employee, entry_time=timezone.now())
        return JsonResponse({'status': 'success', 'message': 'Attendance marked successfully.'})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home_page')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home_page')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import json
@csrf_exempt
def process_attendance_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('imageData')
        employee_id = data.get('employeeId')
        
        # Decode the image
        format, imgstr = image_data.split(';base64,') 
        image_bytes = base64.b64decode(imgstr)
        image = Image.open(BytesIO(image_bytes))
        image = np.array(image.convert('RGB'))
        
        # Attempt face recognition
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            try:
                employee = Employee.objects.get(id=employee_id)
                if employee.face_encoding:
                    known_face_encoding = json.loads(employee.face_encoding)
                    matches = face_recognition.compare_faces([known_face_encoding], face_encodings[0])
                    if matches[0]:
                        # Mark attendance
                        Attendance.objects.create(employee=employee, entry_time=timezone.now())
                        return JsonResponse({'success': True, 'message': 'Attendance marked.'})
            except Employee.DoesNotExist:
                pass

        return JsonResponse({'success': False, 'message': 'Face not recognized or employee not found.'})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
import base64
import json
from io import BytesIO
from PIL import Image
import numpy as np

@csrf_exempt
def verify_employee_face(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        employee_id = data['employeeId']
        image_data = data['imageData']
        format, imgstr = image_data.split(';base64,') 
        image_bytes = base64.b64decode(imgstr)
        
        # Decode the image
        image = Image.open(BytesIO(image_bytes))
        image = np.array(image.convert('RGB'))

        # Attempt face recognition
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            try:
                employee = Employee.objects.get(id=employee_id)
                known_face_encoding = json.loads(employee.face_encoding)
                matches = face_recognition.compare_faces([known_face_encoding], face_encodings[0])
                if matches[0]:
                    # Here, mark the attendance
                    # For example, create a new Attendance record
                    Attendance.objects.create(employee=employee, entry_time=timezone.now())
                    return JsonResponse({'success': True, 'message': 'Face verified and attendance marked.'})
            except Employee.DoesNotExist:
                pass

        return JsonResponse({'success': False, 'message': 'Face not recognized or employee not found.'})
