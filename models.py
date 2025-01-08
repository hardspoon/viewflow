from django.db import models
from viewflow.models import Process

class OnboardingProcess(Process):
    """Model for managing onboarding workflow states and data"""
    
    # Personal Information
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Position Information
    position_title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    start_date = models.DateField()
    
    # Workflow State
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Documents
    offer_letter = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    signed_contract = models.FileField(upload_to='contracts/', null=True, blank=True)
    
    # External Service References
    docuseal_submission_id = models.CharField(max_length=255, null=True, blank=True)
    m365_user_id = models.CharField(max_length=255, null=True, blank=True)
    training_course_id = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Onboarding Process'
        verbose_name_plural = 'Onboarding Processes'
        permissions = [
            ('can_start_onboarding', 'Can start onboarding process'),
            ('can_approve_onboarding', 'Can approve onboarding process'),
            ('can_complete_onboarding', 'Can complete onboarding process'),
        ]
    
    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.position_title}'
