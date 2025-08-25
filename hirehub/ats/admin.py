from django.contrib import admin
from .models import Applicant, JobPosition

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'job_position', 'current_stage', 'source', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('job_position', 'current_stage', 'source', 'created_at')

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active', 'created_at')
