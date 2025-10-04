from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='users')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')

    def __str__(self):
        return self.username

class Company(models.Model):
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=3, default='USD')  # ISO currency code

    def __str__(self):
        return self.name

class Expense(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in company currency
    category = models.CharField(max_length=50)
    description = models.TextField()
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"

class ApprovalRule(models.Model):
    RULE_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('specific', 'Specific Approver'),
        ('hybrid', 'Hybrid'),
    ]
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='approval_rule')
    rule_type = models.CharField(max_length=10, choices=RULE_TYPE_CHOICES)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # e.g., 60 for 60%
    specific_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_rules')

    def __str__(self):
        return f"{self.company.name} - {self.rule_type}"

class ApprovalStep(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='approval_steps')
    step_number = models.PositiveIntegerField()
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='approval_steps')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('expense', 'step_number')

    def __str__(self):
        return f"Step {self.step_number} for {self.expense} - {self.status}"
