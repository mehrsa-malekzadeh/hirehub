# ats/views.py
from django.shortcuts import render
from rest_framework import generics
from .models import Applicant
from .serializers import ApplicantSerializer

# Template Views (serve the HTML pages)
def dashboard(request):
    """Main dashboard showing all applicants"""
    return render(request, 'ats/dashboard.html')

def applicant_detail(request, applicant_id):
    """Individual applicant detail page"""
    return render(request, 'ats/applicant_detail.html', {
        'applicant_id': applicant_id
    })

def new_applicant(request):
    """Add new applicant form"""
    return render(request, 'ats/new_applicant.html')

# API Views (handle data operations)
class ApplicantListCreateAPIView(generics.ListCreateAPIView):
    """GET /api/applicants/ and POST /api/applicants/"""
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    
    def get_queryset(self):
        queryset = Applicant.objects.all()
        
        # Handle search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(tags__icontains=search)
            )
        
        # Handle filtering
        stage = self.request.query_params.get('stage', None)
        if stage:
            queryset = queryset.filter(current_stage=stage)
            
        source = self.request.query_params.get('source', None)
        if source:
            queryset = queryset.filter(source=source)
        
        # Handle sorting
        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset

class ApplicantDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """GET, PATCH, DELETE /api/applicants/{id}/"""
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer