from django.urls import path
from employees.views import (
    employee_list_view,
    employee_create_view,
    employee_update_view,
    employee_delete_view
)

app_name = 'employees'

urlpatterns = [
    path('list/', employee_list_view, name='list'),
    path('create/', employee_create_view, name='create'),
    path('update/<int:pk>/', employee_update_view, name='update'),
    path('delete/<int:pk>/', employee_delete_view, name='delete'),
]
