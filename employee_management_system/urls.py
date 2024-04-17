# employee_management_system/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
     path('accounts/', include('django.contrib.auth.urls')),
    path('', include('employees.urls')),  # Add this line for the root path
]
