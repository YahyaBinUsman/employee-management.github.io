
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('employee_list', views.employee_list, name='employee_list'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('new/', views.employee_new, name='employee_new'),
    path('<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('all_employees/', views.all_employees, name='all_employees'),
    path('<int:pk>/attendance/delete/<int:attendance_id>/', views.delete_attendance, name='delete_attendance'),
    path('attendance/', views.employee_attendance, name='employee_attendance'),
    path('<int:pk>/attendance/', views.employee_attendance, name='employee_attendance_with_pk'),
    path('attendance/delete/<int:pk>/', views.delete_attendance, name='delete_attendance'),
    path('update_exit_time/<int:pk>/', views.update_exit_time, name='update_exit_time'),
    path('calculate_salary/', views.calculate_salary, name='calculate_salary'),
    path('leave_request/', views.leave_request, name='leave_request'),
    path('leave_requests/', views.leave_requests, name='leave_requests'),
    path('leave_requests/', views.leave_requests, name='leave_requests'),
    path('process_leave_status/<int:leave_id>/<str:status>/', views.process_leave_status, name='process_leave_status'),
    path('accounts/login/', views.auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', views.auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('process_attendance_image/', views.process_attendance_image, name='process_attendance_image'),
    path('verify-face/', views.verify_employee_face, name='verify_employee_face'),
     path('check_recent_attendance/<int:employee_id>/', views.check_recent_attendance, name='check_recent_attendance'),
    path('add_entry_time/<int:employee_id>/', views.add_entry_time, name='add_entry_time'),


]
