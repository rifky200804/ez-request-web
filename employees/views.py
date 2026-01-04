from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from employees.models import Employee
from employees.forms import EmployeeForm, EmployeeUserCreationForm

@login_required
def employee_list_view(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'ADMIN':
        messages.error(request, "Access denied. Admins only.")
        return redirect('users:dashboard')
        
    employees_qs = Employee.objects.all().order_by('user__username')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(employees_qs, 10) # 10 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'employees/list.html', {'employees': page_obj})

@login_required
def employee_create_view(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'ADMIN':
        messages.error(request, "Access denied. Admins only.")
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = EmployeeUserCreationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Employee profile and User created successfully")
                return redirect('employees:list')
            except IntegrityError:
                messages.error(request, "Error: Username or data already exists.")
                # Fall through to re-render form with error message (and existing form data)
    else:
        form = EmployeeUserCreationForm()
    return render(request, 'employees/form.html', {'form': form, 'title': 'Create New Employee'})

@login_required
def employee_update_view(request, pk):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'ADMIN':
        messages.error(request, "Access denied. Admins only.")
        return redirect('users:dashboard')

    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee profile updated successfully")
            return redirect('employees:list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/form.html', {'form': form, 'title': 'Update Employee'})

@login_required
def employee_delete_view(request, pk):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'ADMIN':
        messages.error(request, "Access denied. Admins only.")
        return redirect('users:dashboard')

    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, "Employee profile deleted successfully")
        return redirect('employees:list')
    return render(request, 'employees/delete.html', {'employee': employee})
