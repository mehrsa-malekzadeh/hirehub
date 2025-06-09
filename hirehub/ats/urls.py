from django.urls import path
from . import views
from django.views import defaults as default_views

app_name = 'ats'

urlpatterns = [
    # UI Views
    path('', views.dashboard, name='dashboard'),
    path('applicant/<int:applicant_id>/', views.applicant_detail, name='applicant_detail'),
    path('new/', views.new_applicant, name='new_applicant'),
    
    # API Endpoints
    path('api/applicants/', views.ApplicantListCreateAPIView.as_view(), name='api_applicant_list'),
    path('api/applicants/<int:pk>/', views.ApplicantDetailAPIView.as_view(), name='api_applicant_detail'),

    # Temporary test paths for error pages
    path('test-400/', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}, name='test_400'),
    path('test-403/', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied!')}, name='test_403'),
    path('test-404/', default_views.page_not_found, kwargs={'exception': Exception('Page not Found!')}, name='test_404'),
    path('test-500/', default_views.server_error, name='test_500'),
]