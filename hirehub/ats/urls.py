from django.urls import path
from . import views

app_name = 'ats'

urlpatterns = [
    # UI Views
    path('', views.dashboard, name='dashboard'),
    path('applicant/<int:applicant_id>/', views.applicant_detail, name='applicant_detail'),
    path('new/', views.new_applicant, name='new_applicant'),
    
    # API Endpoints
    path('api/applicants/', views.ApplicantListCreateAPIView.as_view(), name='api_applicant_list'),
    path('api/applicants/<int:pk>/', views.ApplicantDetailAPIView.as_view(), name='api_applicant_detail'),
]