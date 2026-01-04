from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from users.forms import UserRegistrationForm, LoginForm, UserUpdateForm
from users.models import User

def welcome_view(request):
    return render(request, 'users/welcome.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('users:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def dashboard_view(request):
    from employees.models import Employee
    from service_requests.models import ServiceRequest
    from django.db.models import Q
    
    employee_count = Employee.objects.count()
    recent_employees = Employee.objects.select_related('user').order_by('-date_hired')[:5]
    
    pending_approvals_count = 0
    total_history_count = 0
    total_requests_count = 0
    recent_requests = []
    recent_approvals = []
    
    if hasattr(request.user, 'employee'):
        employee = request.user.employee
        
        # 1. Logic for RECENT REQUESTS (Karyawan & Manager)
        if employee.role in ['KARYAWAN', 'MANAGER']:
            recent_requests = ServiceRequest.objects.filter(employee=employee).order_by('-created_at')[:5]
            total_requests_count = ServiceRequest.objects.filter(employee=employee).count()
            
        # 2. Logic for RECENT APPROVALS & Counts (Manager & Direktur)
        if employee.role == 'MANAGER':
            # Summary Count
            pending_approvals_count = ServiceRequest.objects.filter(
                manager_approver=employee, 
                manager_status='PENDING'
            ).count()
            
            total_history_count = ServiceRequest.objects.filter(
                manager_approver=employee
            ).exclude(manager_status='PENDING').count()
            
            # Recent Approvals list
            recent_approvals = ServiceRequest.objects.filter(
                manager_approver=employee
            ).order_by('-updated_at')[:5]

        elif employee.role == 'DIREKTUR':
            # Summary Count
            pending_approvals_count = ServiceRequest.objects.filter(
                director_approver=employee, 
                director_status='PENDING'
            ).filter(
                Q(manager_status='APPROVED') | Q(manager_status='NA') | Q(manager_approver__isnull=True)
            ).count()
            
            total_history_count = ServiceRequest.objects.filter(
                director_approver=employee
            ).exclude(director_status='PENDING').count()
            
            # Recent Approvals list
            recent_approvals = ServiceRequest.objects.filter(
                director_approver=employee
            ).order_by('-updated_at')[:5]
            
        # Clean up for Admin/General
        if employee.role == 'ADMIN':
            recent_requests = []
        else:
            recent_employees = []


    return render(request, 'users/dashboard.html', {
        'employee_count': employee_count,
        'recent_employees': recent_employees,
        'recent_requests': recent_requests,
        'recent_approvals': recent_approvals,
        'pending_approvals_count': pending_approvals_count,

        'total_history_count': total_history_count,
        'total_requests_count': total_requests_count
    })



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('users:dashboard')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required
def user_list_view(request):
    users_qs = User.objects.all().order_by('username')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users_qs, 10) # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/list.html', {'users': page_obj})


# Helper to check if user is superuser or updating themselves (optional simple permission)
def is_admin(user):
    return user.is_superuser

@login_required
def user_create_view(request):
    # Only allow admin to create users via this view if desired, or open to all
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully")
            return redirect('users:list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/form.html', {'form': form, 'title': 'Create User'})

@login_required
def user_update_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully")
            return redirect('users:list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'users/form.html', {'form': form, 'title': 'Update User'})

@login_required
def user_delete_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully")
        return redirect('users:list')
    return render(request, 'users/delete.html', {'user': user})
