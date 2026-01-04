from django import forms
from service_requests.models import ServiceRequest
from employees.models import Employee

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['request_type', 'title', 'description', 'amount', 'start_date', 'end_date', 'attachment', 'manager_approver', 'director_approver']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Request Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your request...'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (Reimbursement only)'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'manager_approver': forms.Select(attrs={'class': 'form-select'}),
            'director_approver': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'employee'):
            employee = user.employee
            role = employee.role
            
            # Filter Request Types based on Role
            if role == 'KARYAWAN':
                # Exclude PROPOSAL
                self.fields['request_type'].choices = [
                    c for c in ServiceRequest.REQUEST_TYPES if c[0] != 'PROPOSAL'
                ]
                
                # Must select Manager AND Director
                self.fields['manager_approver'].queryset = Employee.objects.filter(role='MANAGER')
                self.fields['director_approver'].queryset = Employee.objects.filter(role='DIREKTUR')
                self.fields['manager_approver'].required = True
                self.fields['director_approver'].required = True
                
            elif role == 'MANAGER':
                # Manager can request everything, but only needs Director approval
                self.fields['manager_approver'].widget = forms.HiddenInput()
                self.fields['manager_approver'].required = False
                
                self.fields['director_approver'].queryset = Employee.objects.filter(role='DIREKTUR')
                self.fields['director_approver'].required = True

    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get('request_type')
        amount = cleaned_data.get('amount')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if request_type == 'REIMBURSEMENT' and not amount:
            self.add_error('amount', 'Amount is required for Reimbursement requests.')
        
        if request_type == 'LEAVE':
            if not start_date or not end_date:
                if not start_date: self.add_error('start_date', 'Start date is required for Leave requests.')
                if not end_date: self.add_error('end_date', 'End date is required for Leave requests.')
            elif end_date < start_date:
                self.add_error('end_date', 'End date cannot be before start date.')
        
        return cleaned_data
