from rest_framework import serializers
from .models import Applicant

class ApplicantSerializer(serializers.ModelSerializer):
    applicant_id = serializers.IntegerField(source='id', read_only=True)
    
    class Meta:
        model = Applicant
        fields = [
            'id', 'applicant_id', 'name', 'email', 'phone',
            'current_stage', 'source', 'tags', 'resume_file', 'resume_text',
            'interviewers', 'interview_dates', 'comments_ta', 'comments_initial_call',
            'comments_evaluation', 'overall_feedback', 'final_decision',
            'created_at', 'updated_at', 'last_status_update'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_status_update']