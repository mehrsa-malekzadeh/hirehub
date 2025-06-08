# ats/views.py
import json
import logging # Added for logging
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from rest_framework import generics
from .models import Applicant
from .serializers import ApplicantSerializer
from .forms import ApplicantForm

# Template Views (serve the HTML pages)
def dashboard(request):
    """
    Displays the main dashboard with a list of applicants.
    Supports filtering by stage and source, and searching by name, email, or tags.
    """
    queryset = Applicant.objects.all() # Start with all applicants

    # Get filter parameters from the request's query string
    stage = request.GET.get('stage')
    source = request.GET.get('source')
    search_query = request.GET.get('search_query')

    # Apply stage filter if 'stage' parameter is present
    if stage:
        queryset = queryset.filter(current_stage=stage)

    # Apply source filter if 'source' parameter is present
    if source:
        queryset = queryset.filter(source=source)

    # Apply search query if 'search_query' parameter is present
    if search_query:
        # Use Q objects for OR queries: search in name, email, or tags
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # Prepare context for the template
    # Add temporary logging
    logger = logging.getLogger(__name__)
    logger.error(f"Number of applicants in queryset: {len(queryset)}")

    # Serialize the applicants queryset to JSON for client-side rendering
    serializer = ApplicantSerializer(queryset, many=True)
    serialized_data = serializer.data # Store serialized data before dumping to json
    logger.error(f"Serialized data (first 2 items): {serialized_data[:2]}")

    applicants_json = json.dumps(serialized_data, cls=DjangoJSONEncoder)
    logger.error(f"Applicants JSON (first 300 chars): {applicants_json[:300]}")

    context = {
        # 'applicants': queryset, # No longer passing the queryset directly for table rendering
        'applicants_json': applicants_json, # Pass JSON data for JS
        'stage_choices': Applicant.STAGE_CHOICES, # For filter dropdowns
        'source_choices': Applicant.SOURCE_CHOICES, # For filter dropdowns
        'current_stage_filter': stage, # To initialize JS filters
        'current_source_filter': source, # To initialize JS filters
        'current_search_query': search_query, # To initialize JS search
    }
    return render(request, 'ats/dashboard.html', context)

def applicant_detail(request, applicant_id):
    """
    Displays the detailed page for a specific applicant.
    Fetches the applicant by ID or returns a 404 error if not found.
    """
    applicant = get_object_or_404(Applicant, pk=applicant_id)
    context = {
        'applicant': applicant
    }
    return render(request, 'ats/applicant_detail.html', context)

def new_applicant(request):
    """
    Handles the creation of a new applicant.
    If the request method is POST and the form is valid, it saves the new applicant
    and redirects to the applicant's detail page.
    Otherwise, it displays an empty or error-bound form.
    """
    if request.method == 'POST':
        # If data is submitted, create a form instance bound to POST data and files
        form = ApplicantForm(request.POST, request.FILES)
        if form.is_valid():
            # If the form is valid, save the applicant instance
            applicant = form.save()
            # Redirect to the newly created applicant's detail page
            return redirect('ats:applicant_detail', applicant_id=applicant.pk)
        # If form is not valid, it will be re-rendered with errors in the template
    else:
        # For a GET request, create an empty form instance
        form = ApplicantForm()

    context = {
        'form': form
    }
    return render(request, 'ats/new_applicant.html', context)

# API Views (handle data operations)
class ApplicantListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating Applicants.

    GET /api/applicants/:
        Lists all applicants.
        Supports filtering via query parameters:
            - `search`: Search by name, email, or tags (e.g., ?search=John Doe)
            - `stage`: Filter by current stage (e.g., ?stage=Interview Stage)
            - `source`: Filter by source (e.g., ?source=LinkedIn)
        Supports ordering via query parameter:
            - `ordering`: Field to order by (e.g., ?ordering=name or ?ordering=-created_at)
                         Defaults to '-created_at'.

    POST /api/applicants/:
        Creates a new applicant.
        Expects data according to ApplicantSerializer.
        Returns 201 Created on success with applicant data.
        Returns 400 Bad Request on validation errors.
    """
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    
    def get_queryset(self):
        queryset = Applicant.objects.all() # Start with all applicants
        
        # Retrieve query parameters for search, filtering, and ordering
        search = self.request.query_params.get('search', None)
        stage = self.request.query_params.get('stage', None)
        source = self.request.query_params.get('source', None)
        ordering = self.request.query_params.get('ordering', '-created_at') # Default ordering

        # Apply search filter if 'search' parameter is present
        if search:
            # Use Q objects for OR queries: search in name, email, or tags
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # Apply stage filter if 'stage' parameter is present
        if stage:
            queryset = queryset.filter(current_stage=stage)
            
        # Apply source filter if 'source' parameter is present
        if source:
            queryset = queryset.filter(source=source)
        
        # Apply ordering
        queryset = queryset.order_by(ordering)
        
        return queryset

class ApplicantDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a single Applicant.

    GET /api/applicants/{id}/:
        Retrieves a specific applicant by their ID.
        Returns 200 OK with applicant data.
        Returns 404 Not Found if the applicant does not exist.

    PUT /api/applicants/{id}/:
        Updates an existing applicant.
        Expects complete applicant data according to ApplicantSerializer.
        Returns 200 OK on success with updated applicant data.
        Returns 400 Bad Request on validation errors.
        Returns 404 Not Found if the applicant does not exist.

    PATCH /api/applicants/{id}/:
        Partially updates an existing applicant.
        Expects a subset of applicant data according to ApplicantSerializer.
        Returns 200 OK on success with updated applicant data.
        Returns 400 Bad Request on validation errors.
        Returns 404 Not Found if the applicant does not exist.

    DELETE /api/applicants/{id}/:
        Deletes an existing applicant.
        Returns 204 No Content on successful deletion.
        Returns 404 Not Found if the applicant does not exist.
    """
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer