from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from users.forms import UserRegistrationForm, LoginForm, UserUpdateForm
from users.models import User
import uuid
import datetime

def welcome_view(request):
    return render(request, 'users/welcome.html')

def about_view(request):
    return render(request, 'users/about.html')

def contact_view(request):
    if request.method == 'POST':
        messages.success(request, "Your message has been sent successfully! We will get back to you soon.")
        return redirect('users:contact')
    return render(request, 'users/contact.html')

def gallery_view(request):
    return render(request, 'users/gallery.html')

def team_view(request):
    return render(request, 'users/team.html')

def calculate_salary_logic(name, role, religion):
    """
    Helper function to calculate salary, allowances, and Zakat.
    """
    # Base Salary Mapping (Dummy)
    salary_map = {
        'Manager': 15000000,
        'Developer': 10000000,
        'Staff': 6000000,
        'Intern': 2000000
    }
    
    base_salary = salary_map.get(role, 0)
    
    # Allowances
    transport_allowance = 500000 if role != 'Intern' else 100000
    meal_allowance = 1000000 if role != 'Intern' else 300000
    
    gross_salary = base_salary + transport_allowance + meal_allowance
    
    # Zakat Calculation (2.5% if Islam)
    zakat = 0
    if religion == 'Islam' and gross_salary >= 6859394: # Nisab per month assumption (actual varies, simplified here 85g gold / 12)
            zakat = gross_salary * 0.025
            
    net_salary = gross_salary - zakat
    
    return {
        'name': name,
        'role': role,
        'base_salary': base_salary,
        'transport': transport_allowance,
        'meal': meal_allowance,
        'gross': gross_salary,
        'zakat': zakat,
        'net_salary': net_salary,
        'religion': religion
    }

def check_request_view(request):
    """
    View for checking request status (dummy), calculating salary, and simulated approval flow.
    Accessible without login. Uses Session to store list of requests.
    """
    
    # --- DUMMY DATA FOR REQUEST TYPES (DISPLAY PURPOSES) ---
    available_services = [
        {"title": "Pengajuan Proposal", "category": "PROPOSAL", "estimated_time": "3-5 Hari"},
        {"title": "Reimbursement", "category": "REIMBURSEMENT", "estimated_time": "1-2 Minggu"},
        {"title": "Permintaan Cuti", "category": "LEAVE", "estimated_time": "1-2 Hari"},
    ]

    # Initialize Session if not exists
    if 'sim_queue' not in request.session:
        request.session['sim_queue'] = []
    
    # Helper to get queue
    sim_queue = request.session['sim_queue']

    context = {
        'available_services': available_services,
        'result': None, # For Salary Calculation Result
        'sim_elements': sim_queue,
        'sim_stage': request.session.get('sim_stage', 'identity'), 
        'sim_identity': request.session.get('sim_identity', {}),
        'allowed_categories': request.session.get('allowed_categories', [])
    }

    if request.method == "POST":
        # === 0. RESET SIMULATION (Top Priority) ===
        if 'reset_sim' in request.POST:
            request.session['sim_queue'] = []
            request.session['sim_stage'] = 'identity'
            request.session['sim_identity'] = {}
            request.session['allowed_categories'] = []
            return redirect('users:check_request')

        # === 1. SALARY CALCULATION LOGIC ===
        elif 'calculate_salary' in request.POST:
            name = request.POST.get('name')
            role = request.POST.get('role')
            religion = request.POST.get('religion')
            
            context['result'] = calculate_salary_logic(name, role, religion)

        # === 2. SIMULATION: IDENTITY STEP ===
        elif 'start_sim' in request.POST:
            name = request.POST.get('sim_name')
            role = request.POST.get('sim_role')
            
            identity = {'name': name, 'role': role}
            request.session['sim_identity'] = identity
            context['sim_identity'] = identity
            
            if role == 'Director':
                request.session['sim_stage'] = 'director_approval'
                # Generate dummy requests only if empty to show something
                if not sim_queue:
                    dummy_req = {
                        'id': str(uuid.uuid4()),
                        'title': 'Anggaran Pemasaran Q4',
                        'description': 'Proposal untuk biaya kampanye pemasaran akhir tahun.',
                        'category': 'PROPOSAL',
                        'estimated_time': '1 Minggu',
                        'status': 'MENUNGGU_PERSETUJUAN',
                        'submitted_by': 'Alice Manajer',
                        'submitter_role': 'Manager',
                        'submitted_at': '2 Jam Lalu',
                        'amount': '150000000',
                        'manager_status': 'APPROVED'
                    }
                    sim_queue.append(dummy_req)
                    request.session['sim_queue'] = sim_queue
                
            elif role == 'Manager':
                 request.session['sim_stage'] = 'manager_menu'
                 
            else: # Staff
                request.session['sim_stage'] = 'create_request'
                request.session['allowed_categories'] = ['REIMBURSEMENT', 'LEAVE']

        # === 3. MANAGER MENU ACTION ===
        elif 'manager_action' in request.POST:
             # Identity already in session
             action = request.POST.get('manager_choice')
             
             if action == 'create':
                 request.session['sim_stage'] = 'create_request'
                 request.session['allowed_categories'] = ['PROPOSAL', 'REIMBURSEMENT', 'LEAVE']
             elif action == 'approve':
                 request.session['sim_stage'] = 'manager_approval_list'
                 # Simulate a request from a Staff if empty
                 if not sim_queue:
                     dummy_req = {
                        'id': str(uuid.uuid4()),
                        'title': 'Charger Laptop Baru',
                        'description': 'Charger saya saat ini rusak.',
                        'category': 'REIMBURSEMENT',
                        'estimated_time': '2 Hari',
                        'status': 'MENUNGGU_PERSETUJUAN',
                        'submitted_by': 'Bob Staf',
                        'submitter_role': 'Staff',
                        'submitted_at': '1 Jam Lalu',
                        'amount': '450000',
                        'manager_status': 'PENDING'
                    }
                     sim_queue.append(dummy_req)
                     request.session['sim_queue'] = sim_queue

        # === 4. SIMULATION: SUBMIT REQUEST (Staff/Manager) ===
        elif 'submit_sim_request' in request.POST:
            req_type = request.POST.get('category')
            req_title = request.POST.get('title')
            req_desc = request.POST.get('description')
            req_amount = request.POST.get('amount')
            req_start_date = request.POST.get('start_date')
            req_end_date = request.POST.get('end_date')
            
            if req_type == 'PROPOSAL': estimation = "5 Hari"
            elif req_type == 'REIMBURSEMENT': estimation = "7 Hari"
            elif req_type == 'LEAVE': estimation = "2 Hari"
            else: estimation = "3 Hari"
            
            current_identity = request.session.get('sim_identity', {})
            
            new_req = {
                'id': str(uuid.uuid4()),
                'title': req_title,
                'description': req_desc,
                'category': req_type,
                'estimated_time': estimation,
                'status': 'MENUNGGU_PERSETUJUAN',
                'submitted_by': current_identity.get('name', 'Unknown'),
                'submitter_role': current_identity.get('role', 'Staff'),
                'submitted_at': 'Baru Saja',
                'amount': req_amount,
                'start_date': req_start_date,
                'end_date': req_end_date,
                'manager_status': 'PENDING' # Default pending
            }
            
            if current_identity.get('role') == 'Manager':
                new_req['manager_status'] = 'APPROVED' 
            
            sim_queue.append(new_req)
            request.session['sim_queue'] = sim_queue
            
            request.session['sim_stage'] = 'submitted_wait'

        # === 5. SIMULATION: APPROVAL (Manager/Director) ===
        elif 'approve_sim_request' in request.POST:
             req_id = request.POST.get('req_id')
             action = request.POST.get('action') # 'approve' or 'reject'
             manager_comment = request.POST.get('manager_comment')
             
             final_status = 'DISETUJUI' if action == 'approve' else 'DITOLAK'
             
             # Find and update
             for req in sim_queue:
                 if req['id'] == req_id:
                     req['status'] = final_status
                     req['manager_comment'] = manager_comment
                     req['approved_at'] = 'Baru Saja'
                     
                     if action == 'approve':
                         req['manager_status'] = 'APPROVED'
                     else:
                         req['manager_status'] = 'REJECTED'
                     
                     break
             
             request.session['sim_queue'] = sim_queue
             # Stay on list
             # request.session['sim_stage'] = 'completed'

        # === 6. SWITCH USER (Keep Data) ===
        elif 'switch_user' in request.POST:
            request.session['sim_stage'] = 'identity'
            request.session['sim_identity'] = {}
            request.session['allowed_categories'] = []
            return redirect('users:check_request')

    # Update context from session state
    context['sim_stage'] = request.session.get('sim_stage', 'identity')
    context['sim_identity'] = request.session.get('sim_identity', {})
    context['allowed_categories'] = request.session.get('allowed_categories', [])
    context['sim_elements'] = request.session.get('sim_queue', [])

    return render(request, 'users/check_request.html', context)

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
