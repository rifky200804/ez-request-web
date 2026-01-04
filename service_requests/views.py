from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from service_requests.models import ServiceRequest
from service_requests.forms import ServiceRequestForm

@login_required
def request_list_view(request):
    # Only show requests belonging to the logged-in employee
    if not hasattr(request.user, 'employee'):
        messages.error(request, "You must be an employee to view requests.")
        return redirect('users:dashboard')
        
    requests = ServiceRequest.objects.filter(employee=request.user.employee).order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(requests, 10) # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'service_requests/list.html', {'requests': page_obj})

@login_required
def request_create_view(request):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "You must be an employee to submit requests.")
        return redirect('users:dashboard')

    employee = request.user.employee
    if employee.role not in ['KARYAWAN', 'MANAGER']:
        messages.error(request, "Directors and Admins cannot submit requests.")
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.employee = request.user.employee
            
            # If Manager is submitting, Manager Approval is Not Applicable
            if request.user.employee.role == 'MANAGER':
                service_request.manager_status = 'NA'
                
            service_request.save()
            messages.success(request, "Request submitted successfully.")
            return redirect('service_requests:list')
    else:
        # Pre-fill type if provided in GET params
        initial_type = request.GET.get('type')
        form = ServiceRequestForm(initial={'request_type': initial_type}, user=request.user)
        
    return render(request, 'service_requests/form.html', {'form': form, 'title': 'New Service Request'})

@login_required
def request_delete_view(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk, employee=request.user.employee)
    
    if service_request.status != 'PENDING':
        messages.error(request, "Cannot delete processed requests.")
        return redirect('service_requests:list')
        
    if request.method == 'POST':
        service_request.delete()
        messages.success(request, "Request withdrawn successfully.")
        return redirect('service_requests:list')
    
    return render(request, 'service_requests/delete.html', {'object': service_request})

@login_required
@login_required
def approval_list_view(request):
    if not hasattr(request.user, 'employee'):
        return redirect('users:dashboard')
    
    employee = request.user.employee
    
    # 1. PENDING APPROVALS
    if employee.role == 'MANAGER':
        pending_list = ServiceRequest.objects.filter(
            manager_approver=employee, 
            manager_status='PENDING'
        ).order_by('created_at')
        
        history_list = ServiceRequest.objects.filter(
            manager_approver=employee
        ).exclude(manager_status='PENDING').order_by('-updated_at')
        
    elif employee.role == 'DIREKTUR':
        pending_list = ServiceRequest.objects.filter(
            director_approver=employee, 
            director_status='PENDING'
        ).filter(
            Q(manager_status='APPROVED') | Q(manager_status='NA') | Q(manager_approver__isnull=True)
        ).order_by('created_at')
        
        history_list = ServiceRequest.objects.filter(
            director_approver=employee
        ).exclude(director_status='PENDING').order_by('-updated_at')
    else:
        pending_list = []
        history_list = []

    # Pagination for Pending Approvals
    from django.core.paginator import Paginator
    paginator_pending = Paginator(pending_list, 10)
    page_pending = request.GET.get('page_pending')
    pending_list_obj = paginator_pending.get_page(page_pending)
    
    # Pagination for History
    paginator_history = Paginator(history_list, 10)
    page_history = request.GET.get('page_history')
    history_list_obj = paginator_history.get_page(page_history)

    return render(request, 'service_requests/approval_list.html', {
        'approval_list': pending_list_obj,
        'history_list': history_list_obj
    })

@login_required
def request_approve_view(request, pk):
    if request.method != 'POST':
        return redirect('users:dashboard')
        
    employee = request.user.employee
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    action = request.POST.get('action')
    feedback = request.POST.get('feedback', '')
    status_val = 'APPROVED' if action == 'approve' else 'REJECTED'

    # Use IDs for safer comparison
    is_manager = service_request.manager_approver_id == employee.id
    is_director = service_request.director_approver_id == employee.id

    if is_manager and service_request.manager_status == 'PENDING':
        service_request.manager_status = status_val
        service_request.feedback = f"Manager: {feedback}" if feedback else None
        if status_val == 'REJECTED':
            service_request.status = 'REJECTED'
        service_request.save()
        messages.success(request, f"Request {status_val.lower()} successfully.")
        
    elif is_director and service_request.director_status == 'PENDING':
        # Conditions: 
        # 1. Manager Status is explicitly APPROVED
        # 2. Manager Status is explicitly NA (Manager request)
        # 3. Manager Approver is None (Implicit Not Applicable)
        can_approve = False
        if service_request.manager_status in ['APPROVED', 'NA']:
            can_approve = True
        elif service_request.manager_approver is None:
            # If no manager assigned, implicit NA
            can_approve = True
            
        if can_approve:
            service_request.director_status = status_val
            service_request.status = status_val # Final status matches Director
            current_feedback = service_request.feedback + "\n" if service_request.feedback else ""
            service_request.feedback = f"{current_feedback}Director: {feedback}" if feedback else service_request.feedback
            service_request.save()
            messages.success(request, f"Request {status_val.lower()} successfully.")
        else:
            messages.error(request, "Cannot process this request. Manager approval is pending.")
    else:
        messages.error(request, "Invalid approval action.")
    
    return redirect('service_requests:approvals')
