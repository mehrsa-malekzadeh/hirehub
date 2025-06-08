from django.contrib import admin
from .models import Applicant

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'current_stage', 'source', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('current_stage', 'source', 'created_at')
