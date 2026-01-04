from django.db import models
from django.conf import settings

class Employee(models.Model):
    ROLE_CHOICES = (
        ('KARYAWAN', 'Karyawan'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Admin'),
        ('DIREKTUR', 'Direktur'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee')
    position = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='KARYAWAN')
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    date_hired = models.DateField()

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) - {self.position}"
