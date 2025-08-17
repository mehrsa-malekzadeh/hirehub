from django.urls import path
from . import views

app_name = 'ats'

urlpatterns = [
    # UI Views
    path('', views.dashboard, name='dashboard'),
    path('applicant/<int:applicant_id>/', views.applicant_detail, name='applicant_detail'),
    path('new/', views.new_applicant, name='new_applicant'),

    # Job Position URLs
    path('positions/', views.job_position_list, name='job_position_list'),
    path('positions/new/', views.new_job_position, name='new_job_position'),
    path('positions/<int:pk>/', views.job_position_detail, name='job_position_detail'),
    path('positions/<int:pk>/edit/', views.edit_job_position, name='edit_job_position'),
    
    # API Endpoints
    path('api/applicants/', views.ApplicantListCreateAPIView.as_view(), name='api_applicant_list'),
    path('api/applicants/<int:pk>/', views.ApplicantDetailAPIView.as_view(), name='api_applicant_detail'),
    path('api/positions/', views.JobPositionListCreateAPIView.as_view(), name='api_job_position_list'),
    path('api/positions/<int:pk>/', views.JobPositionDetailAPIView.as_view(), name='api_job_position_detail'),
]