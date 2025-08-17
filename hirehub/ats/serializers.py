from rest_framework import serializers
from .models import Applicant, JobPosition

class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = '__all__'

class ApplicantSerializer(serializers.ModelSerializer):
    job_position_details = JobPositionSerializer(source='job_position', read_only=True)
    applicant_id = serializers.IntegerField(source='id', read_only=True)
    
    class Meta:
        model = Applicant
        fields = [
            'id', 'applicant_id', 'name', 'email', 'phone', 'job_position', 'job_position_details',
            'current_stage', 'source', 'tags', 'resume_file', 'resume_text',
            'interviewers', 'interview_dates', 'comments_ta', 'comments_initial_call',
            'comments_evaluation', 'overall_feedback', 'final_decision',
            'created_at', 'updated_at', 'last_status_update'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_status_update']