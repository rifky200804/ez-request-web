from django.db import models
from employees.models import Employee

class ServiceRequest(models.Model):
    REQUEST_TYPES = (
        ('PROPOSAL', 'Proposal'),
        ('REIMBURSEMENT', 'Reimbursement'),
        ('LEAVE', 'Leave'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    attachment = models.FileField(upload_to='requests/attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Approval Workflow
    manager_approver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_requests')
    director_approver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='director_requests')
    
    manager_status = models.CharField(max_length=15, choices=STATUS_CHOICES + (('NA', 'Not Applicable'),), default='PENDING')
    director_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    
    # Feedback/Comments
    feedback = models.TextField(blank=True, null=True, help_text="Reason for rejection or approval notes")

    # Type-Specific Fields

    # Type-Specific Fields
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Required for Reimbursement")
    start_date = models.DateField(blank=True, null=True, help_text="Required for Leave")
    end_date = models.DateField(blank=True, null=True, help_text="Required for Leave")

    def __str__(self):
        return f"{self.get_request_type_display()}: {self.title} - {self.status}"
