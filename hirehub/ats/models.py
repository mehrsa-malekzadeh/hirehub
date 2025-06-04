# ats/models.py
from django.db import models

class Applicant(models.Model):
    STAGE_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Interview Stage', 'Interview Stage'),
        ('Technical Assessment', 'Technical Assessment'),
        ('Final Interview', 'Final Interview'),
        ('Offer Extended', 'Offer Extended'),
        ('Hired', 'Hired'),
        ('Rejected', 'Rejected'),
    ]
    
    SOURCE_CHOICES = [
        ('LinkedIn', 'LinkedIn'),
        ('Indeed', 'Indeed'),
        ('Referral', 'Referral'),
        ('Company Website', 'Company Website'),
        ('Job Board', 'Job Board'),
        ('Other', 'Other'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Application Details
    current_stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='Submitted')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    
    # Resume
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_text = models.TextField(blank=True)
    
    # Interview Information
    interviewers = models.TextField(blank=True)
    interview_dates = models.TextField(blank=True)
    
    # Comments and Feedback
    comments_ta = models.TextField(blank=True, verbose_name="Technical Assessment Comments")
    comments_initial_call = models.TextField(blank=True, verbose_name="Initial Call Comments")
    comments_evaluation = models.TextField(blank=True, verbose_name="Evaluation Comments")
    overall_feedback = models.TextField(blank=True)
    final_decision = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_status_update = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.current_stage}"
    
    class Meta:
        ordering = ['-created_at']