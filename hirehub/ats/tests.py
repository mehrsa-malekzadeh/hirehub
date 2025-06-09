from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.db.models import Q # Import Q
from .models import Applicant

class ApplicantModelTests(TestCase):

    def setUp(self):
        """Set up data for tests."""
        self.valid_applicant_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'source': 'LinkedIn',
            'tags': 'developer, python',
            'resume_text': 'Experienced Python developer.',
            'interviewers': 'Jane Smith',
            'interview_dates': '2024-08-01',
            'comments_ta': 'Good technical skills.',
            'comments_initial_call': 'Positive initial call.',
            'comments_evaluation': 'Strong candidate.',
            'overall_feedback': 'Recommend for next stage.',
            'final_decision': 'Pending',
        }

        # Minimal data for an applicant
        self.minimal_applicant_data = {
            'name': 'Jane Roe',
            'email': 'jane.roe@example.com',
            'source': 'Indeed', # Source is a required field
        }

    def test_create_applicant_with_all_fields(self):
        """Test creating an Applicant instance with all specified fields."""
        applicant = Applicant.objects.create(**self.valid_applicant_data)
        self.assertEqual(applicant.name, 'John Doe')
        self.assertEqual(applicant.email, 'john.doe@example.com')
        self.assertEqual(applicant.phone, '1234567890')
        self.assertEqual(applicant.source, 'LinkedIn')
        self.assertEqual(applicant.tags, 'developer, python')
        self.assertEqual(applicant.resume_text, 'Experienced Python developer.')
        self.assertEqual(applicant.current_stage, 'Submitted') # Check default stage
        # Check a few more fields to be thorough
        self.assertEqual(applicant.interviewers, 'Jane Smith')
        self.assertEqual(applicant.overall_feedback, 'Recommend for next stage.')
        self.assertIsNotNone(applicant.created_at)
        self.assertIsNotNone(applicant.updated_at)

    def test_create_applicant_with_minimal_data(self):
        """Test creating an Applicant instance with minimal required data."""
        applicant = Applicant.objects.create(**self.minimal_applicant_data)
        self.assertEqual(applicant.name, 'Jane Roe')
        self.assertEqual(applicant.email, 'jane.roe@example.com')
        self.assertEqual(applicant.source, 'Indeed')
        self.assertEqual(applicant.phone, '')  # Default blank
        self.assertEqual(applicant.tags, '')  # Default blank
        self.assertEqual(applicant.resume_text, '')  # Default blank
        self.assertEqual(applicant.current_stage, 'Submitted') # Check default stage
        self.assertIsNotNone(applicant.created_at)
        self.assertIsNotNone(applicant.updated_at)

    def test_applicant_current_stage_default(self):
        """Test that the default value for current_stage is 'Submitted'."""
        applicant = Applicant.objects.create(**self.minimal_applicant_data)
        self.assertEqual(applicant.current_stage, 'Submitted')

    def test_applicant_str_method(self):
        """Test the __str__ method of the Applicant model."""
        applicant = Applicant.objects.create(name="Test User", email="test@example.com", source="Other")
        # Based on the model: return f"{self.name} - {self.current_stage}"
        self.assertEqual(str(applicant), "Test User - Submitted")

    def test_applicant_invalid_email(self):
        """Test that creating an Applicant with an invalid email raises ValidationError."""
        invalid_data = self.minimal_applicant_data.copy()
        invalid_data['email'] = 'not-an-email'

        # EmailField performs validation at the model field level.
        # This validation is run during the clean_fields() method,
        # which is called by full_clean(). Direct .create() might bypass
        # full_clean() for some fields if they have defaults or are blank=True
        # and not explicitly provided.
        # For robust testing of field validation, it's best to instantiate
        # the model and call full_clean().

        applicant = Applicant(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            applicant.full_clean() # This will trigger field validation including EmailField

        self.assertIn('email', context.exception.message_dict)

    def test_applicant_name_max_length(self):
        """Test that the name field respects max_length=200."""
        long_name = 'a' * 201
        invalid_data = self.minimal_applicant_data.copy()
        invalid_data['name'] = long_name

        applicant = Applicant(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            applicant.full_clean() # Use full_clean to trigger model validation

        self.assertIn('name', context.exception.message_dict)
        # Check that a name of exactly 200 characters is fine
        valid_name = 'b' * 200
        valid_data = self.minimal_applicant_data.copy()
        valid_data['name'] = valid_name
        try:
            applicant_valid_name = Applicant(**valid_data)
            applicant_valid_name.full_clean() # Should not raise
            applicant_valid_name.save() # Try saving to be sure
        except ValidationError:
            self.fail("Applicant name with 200 characters should be valid.")

    def test_applicant_phone_optional(self):
        """Test that phone field is optional (blank=True)."""
        data = self.minimal_applicant_data.copy()
        # Ensure phone is not in minimal_applicant_data or set to ''
        if 'phone' in data:
            del data['phone']

        applicant = Applicant.objects.create(**data)
        self.assertEqual(applicant.phone, '') # Default blank value

    def test_applicant_tags_optional(self):
        """Test that tags field is optional (blank=True)."""
        data = self.minimal_applicant_data.copy()
        if 'tags' in data:
            del data['tags']

        applicant = Applicant.objects.create(**data)
        self.assertEqual(applicant.tags, '') # Default blank value

    def test_resume_file_optional(self):
        """Test that resume_file field is optional."""
        data = self.minimal_applicant_data.copy()
        # resume_file is FileField(upload_to='resumes/', blank=True, null=True)
        applicant = Applicant.objects.create(**data)
        self.assertIsNone(applicant.resume_file.name) # No file uploaded

    def test_resume_text_optional(self):
        """Test that resume_text field is optional."""
        data = self.minimal_applicant_data.copy()
        applicant = Applicant.objects.create(**data)
        self.assertEqual(applicant.resume_text, '')


import json
from django.urls import reverse
from django.test import Client
# Applicant model is already imported

class DashboardViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('ats:dashboard')

        # Common applicants for some tests - ensure they have all required fields
        self.app1 = Applicant.objects.create(
            name="Alice Wonderland",
            email="alice@example.com",
            source="LinkedIn",
            current_stage="Submitted",
            tags="python, django"
        )
        self.app2 = Applicant.objects.create(
            name="Bob The Builder",
            email="bob@example.com",
            source="Indeed",
            current_stage="Under Review",
            tags="java, spring"
        )
        self.app3 = Applicant.objects.create(
            name="Charlie Brown",
            email="charlie@example.com",
            source="Referral",
            current_stage="Submitted", # Same stage as Alice for stage filter test
            tags="python, javascript"
        )

    def test_dashboard_get_request_status_code_ok(self):
        """Test GET request to dashboard returns HTTP 200 OK."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        """Test dashboard view uses the correct template."""
        response = self.client.get(self.dashboard_url)
        self.assertTemplateUsed(response, 'ats/dashboard.html')

    def test_dashboard_context_variables_present(self):
        """Test that essential variables are in the context."""
        response = self.client.get(self.dashboard_url)
        self.assertIn('applicants_json', response.context)
        self.assertIn('stage_choices', response.context)
        self.assertIn('source_choices', response.context)

        # Check choices match model
        self.assertEqual(list(response.context['stage_choices']), list(Applicant.STAGE_CHOICES))
        self.assertEqual(list(response.context['source_choices']), list(Applicant.SOURCE_CHOICES))

    def test_dashboard_filter_by_stage(self):
        """Test filtering applicants by stage."""
        # app1: Submitted, app2: Under Review, app3: Submitted
        response = self.client.get(self.dashboard_url, {'stage': 'Submitted'})
        self.assertEqual(response.status_code, 200)

        applicants_json = response.context['applicants_json']
        data = json.loads(applicants_json)

        self.assertEqual(len(data), 2)
        applicant_names = sorted([item['name'] for item in data])
        self.assertEqual(applicant_names, sorted([self.app1.name, self.app3.name]))
        for item in data:
            self.assertEqual(item['current_stage'], 'Submitted')

        response_under_review = self.client.get(self.dashboard_url, {'stage': 'Under Review'})
        self.assertEqual(response_under_review.status_code, 200)
        data_under_review = json.loads(response_under_review.context['applicants_json'])
        self.assertEqual(len(data_under_review), 1)
        self.assertEqual(data_under_review[0]['name'], self.app2.name)
        self.assertEqual(data_under_review[0]['current_stage'], 'Under Review')

    def test_dashboard_filter_by_source(self):
        """Test filtering applicants by source."""
        # app1: LinkedIn, app2: Indeed, app3: Referral
        response = self.client.get(self.dashboard_url, {'source': 'LinkedIn'})
        self.assertEqual(response.status_code, 200)

        applicants_json = response.context['applicants_json']
        data = json.loads(applicants_json)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], self.app1.name)
        self.assertEqual(data[0]['source'], 'LinkedIn')

        response_indeed = self.client.get(self.dashboard_url, {'source': 'Indeed'})
        data_indeed = json.loads(response_indeed.context['applicants_json'])
        self.assertEqual(len(data_indeed), 1)
        self.assertEqual(data_indeed[0]['name'], self.app2.name)
        self.assertEqual(data_indeed[0]['source'], 'Indeed')

    def test_dashboard_search_by_name(self):
        """Test searching applicants by name."""
        response = self.client.get(self.dashboard_url, {'search_query': 'Alice'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.context['applicants_json'])
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], self.app1.name)

        response_no_match = self.client.get(self.dashboard_url, {'search_query': 'NonExistentName'})
        data_no_match = json.loads(response_no_match.context['applicants_json'])
        self.assertEqual(len(data_no_match), 0)

        # Test partial match
        response_partial = self.client.get(self.dashboard_url, {'search_query': 'Wonder'})
        data_partial = json.loads(response_partial.context['applicants_json'])
        self.assertEqual(len(data_partial), 1)
        self.assertEqual(data_partial[0]['name'], self.app1.name)


    def test_dashboard_search_by_email(self):
        """Test searching applicants by email."""
        response = self.client.get(self.dashboard_url, {'search_query': 'bob@example.com'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.context['applicants_json'])
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], self.app2.email)

        # Test partial match (e.g. by domain)
        response_partial = self.client.get(self.dashboard_url, {'search_query': 'example.com'})
        data_partial = json.loads(response_partial.context['applicants_json'])
        self.assertEqual(len(data_partial), 3) # All three use example.com

    def test_dashboard_search_by_tags(self):
        """Test searching applicants by tags."""
        # app1: "python, django", app2: "java, spring", app3: "python, javascript"
        response_python = self.client.get(self.dashboard_url, {'search_query': 'python'})
        self.assertEqual(response_python.status_code, 200)
        data_python = json.loads(response_python.context['applicants_json'])
        self.assertEqual(len(data_python), 2) # Alice and Charlie have 'python'
        names_python = sorted([item['name'] for item in data_python])
        self.assertEqual(names_python, sorted([self.app1.name, self.app3.name]))

        response_django = self.client.get(self.dashboard_url, {'search_query': 'django'})
        self.assertEqual(response_django.status_code, 200)
        data_django = json.loads(response_django.context['applicants_json'])
        self.assertEqual(len(data_django), 1)
        self.assertEqual(data_django[0]['name'], self.app1.name)

        response_spring = self.client.get(self.dashboard_url, {'search_query': 'spring'})
        self.assertEqual(response_spring.status_code, 200)
        data_spring = json.loads(response_spring.context['applicants_json'])
        self.assertEqual(len(data_spring), 1)
        self.assertEqual(data_spring[0]['name'], self.app2.name)

    def test_dashboard_search_by_tag_exact_match(self):
        """Test searching by an exact tag when multiple tags exist."""
        Applicant.objects.create(
            name="David Copperfield", email="david@example.com", source="Other", tags="python"
        )
        Applicant.objects.create(
            name="Eve Harrington", email="eve@example.com", source="Other", tags="pythonista"
        )

        response = self.client.get(self.dashboard_url, {'search_query': 'python'})
        data = json.loads(response.context['applicants_json'])
        # Expecting Alice, Charlie, David, and Eve (since 'python' is in 'pythonista')
        self.assertEqual(len(data), 4)
        names = sorted([item['name'] for item in data])
        self.assertIn("Alice Wonderland", names)
        self.assertIn("Charlie Brown", names)
        self.assertIn("David Copperfield", names)
        self.assertIn("Eve Harrington", names) # Eve has 'pythonista'

        response_exact = self.client.get(self.dashboard_url, {'search_query': 'pythonista'})
        data_exact = json.loads(response_exact.context['applicants_json'])
        self.assertEqual(len(data_exact), 1)
        self.assertEqual(data_exact[0]['name'], "Eve Harrington")

    def test_dashboard_empty_search_returns_all(self):
        """Test that an empty search query returns all applicants."""
        response = self.client.get(self.dashboard_url, {'search_query': ''})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.context['applicants_json'])
        # self.app1, self.app2, self.app3 are created in setUp
        self.assertEqual(len(data), Applicant.objects.count())
        self.assertEqual(len(data), 3)


    def test_dashboard_filter_and_search_combined(self):
        """Test combined filtering by stage and searching by name."""
        # This part uses the data from setUp:
        # self.app1: Alice (Submitted, python), self.app3: Charlie (Submitted, python)
        # self.app2: Bob (Under Review, java)

        # Test 1: Filter by stage 'Submitted' and search for 'Alice'
        response_alice = self.client.get(self.dashboard_url, {'stage': 'Submitted', 'search_query': 'Alice'})
        self.assertEqual(response_alice.status_code, 200)
        data_alice = json.loads(response_alice.context['applicants_json'])
        self.assertEqual(len(data_alice), 1)
        self.assertEqual(data_alice[0]['name'], self.app1.name) # Check it's Alice

        # Test 2: Filter by stage 'Submitted' and search for 'python'
        response_python_submitted = self.client.get(self.dashboard_url, {'stage': 'Submitted', 'search_query': 'python'})
        self.assertEqual(response_python_submitted.status_code, 200)
        data_python_submitted = json.loads(response_python_submitted.context['applicants_json'])
        self.assertEqual(len(data_python_submitted), 2) # Alice and Charlie have 'python' and are 'Submitted'
        names_python_submitted = sorted([item['name'] for item in data_python_submitted])
        self.assertEqual(names_python_submitted, sorted([self.app1.name, self.app3.name]))

        # Test 3: The problematic case - Filter by stage 'Submitted' and search for 'java'
        # For this specific case, clear existing Applicant data and create a very controlled set
        # to ensure no interference.
        Applicant.objects.all().delete()

        Applicant.objects.create(
            name="TestAlice Submitted Python", email="test_alice_s_p@example.com", source="Other",
            current_stage="Submitted", tags="python"
        )
        Applicant.objects.create(
            name="TestBob Review Java", email="test_bob_r_j@example.com", source="Other",
            current_stage="Under Review", tags="java" # This one has 'java' but is 'Under Review'
        )
        Applicant.objects.create(
            name="TestCharlie Submitted Nothing", email="test_charlie_s_n@example.com", source="Other",
            current_stage="Submitted", tags="none"
        )
        self.assertEqual(Applicant.objects.count(), 3) # Ensure clean setup for this part

        response_java_submitted = self.client.get(self.dashboard_url, {'stage': 'Submitted', 'search_query': 'java'})
        self.assertEqual(response_java_submitted.status_code, 200)

        # For debugging, print if needed. Should be empty.
        # print(f"\nDEBUG (Combined Test): Applicants JSON for stage='Submitted', search_query='java': {response_java_submitted.context['applicants_json']}\n")

        data_java_submitted = json.loads(response_java_submitted.context['applicants_json'])
        self.assertEqual(len(data_java_submitted), 0, "Should be 0 applicants matching stage 'Submitted' and search 'java'")


from django.core.files.uploadedfile import SimpleUploadedFile

class ApplicantDetailViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.applicant = Applicant.objects.create(
            name="Detail Applicant",
            email="detail@example.com",
            source="LinkedIn",
            current_stage="Interview Stage",
            tags="c++, qt"
        )
        self.detail_url = reverse('ats:applicant_detail', args=[self.applicant.pk])
        self.non_existent_url = reverse('ats:applicant_detail', args=[9999]) # Assuming 9999 does not exist

    def test_applicant_detail_view_get_valid_id_status_ok(self):
        """Test GET request with valid applicant ID returns 200 OK."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_applicant_detail_view_uses_correct_template(self):
        """Test applicant_detail view uses ats/applicant_detail.html."""
        response = self.client.get(self.detail_url)
        self.assertTemplateUsed(response, 'ats/applicant_detail.html')

    def test_applicant_detail_view_context_has_correct_applicant(self):
        """Test context contains the correct applicant object."""
        response = self.client.get(self.detail_url)
        self.assertIn('applicant', response.context)
        self.assertEqual(response.context['applicant'], self.applicant)
        self.assertEqual(response.context['applicant'].name, "Detail Applicant")

    def test_applicant_detail_view_get_invalid_id_status_404(self):
        """Test GET request with invalid applicant ID returns 404 Not Found."""
        response = self.client.get(self.non_existent_url)
        self.assertEqual(response.status_code, 404)


class NewApplicantViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.new_applicant_url = reverse('ats:new_applicant')
        # Minimal valid data for a new applicant POST request
        self.valid_post_data = {
            'name': 'New Candidate',
            'email': 'new.candidate@example.com',
            'source': 'Company Website', # Source is a required field
            # Optional fields can be added here if needed for specific tests
            'phone': '1234567890',
            'tags': 'new, fresh',
            'resume_text': 'A promising new candidate.',
        }

    def test_new_applicant_view_get_status_ok(self):
        """Test GET request to new_applicant view returns 200 OK."""
        response = self.client.get(self.new_applicant_url)
        self.assertEqual(response.status_code, 200)

    def test_new_applicant_view_uses_correct_template(self):
        """Test new_applicant view uses ats/new_applicant.html."""
        response = self.client.get(self.new_applicant_url)
        self.assertTemplateUsed(response, 'ats/new_applicant.html')
        self.assertIn('form', response.context) # Check form is in context

    def test_new_applicant_view_post_valid_data_creates_applicant_and_redirects(self):
        """Test POSTing valid data creates an applicant and redirects."""
        initial_applicant_count = Applicant.objects.count()

        # Prepare data with a file upload
        resume_content = b"This is a dummy resume file content."
        resume_file = SimpleUploadedFile(
            name="test_resume.txt",
            content=resume_content,
            content_type="text/plain"
        )
        post_data_with_file = self.valid_post_data.copy()
        post_data_with_file['resume_file'] = resume_file

        response = self.client.post(self.new_applicant_url, post_data_with_file, format='multipart')

        self.assertEqual(Applicant.objects.count(), initial_applicant_count + 1)
        new_applicant = Applicant.objects.latest('created_at')

        self.assertEqual(new_applicant.name, 'New Candidate')
        self.assertEqual(new_applicant.email, 'new.candidate@example.com')
        self.assertEqual(new_applicant.source, 'Company Website')

        # Debugging output for the resume file
        print(f"\nDEBUG: new_applicant.resume_file: {new_applicant.resume_file}")
        if hasattr(new_applicant.resume_file, 'name'):
            print(f"DEBUG: new_applicant.resume_file.name: {new_applicant.resume_file.name}")
        else:
            print("DEBUG: new_applicant.resume_file has no 'name' attribute.")

        # Check that the file name starts with the upload_to path and contains the original name part
        self.assertTrue(new_applicant.resume_file.name.startswith('resumes/test_resume'))
        self.assertTrue(new_applicant.resume_file.name.endswith('.txt')) # Check extension

        # Check file content (optional, but good for completeness)
        with new_applicant.resume_file.open('rb') as f:
            self.assertEqual(f.read(), resume_content)

        # Check for redirect to the applicant_detail page
        expected_redirect_url = reverse('ats:applicant_detail', args=[new_applicant.pk])
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

    def test_new_applicant_view_post_valid_data_minimal(self):
        """Test POSTing minimal valid data creates an applicant."""
        initial_applicant_count = Applicant.objects.count()
        minimal_data = {
            'name': 'Minimal Candidate',
            'email': 'minimal.candidate@example.com',
            'source': 'Other',
        }
        response = self.client.post(self.new_applicant_url, minimal_data)
        self.assertEqual(Applicant.objects.count(), initial_applicant_count + 1)
        new_applicant = Applicant.objects.get(email='minimal.candidate@example.com')
        self.assertEqual(new_applicant.name, 'Minimal Candidate')
        expected_redirect_url = reverse('ats:applicant_detail', args=[new_applicant.pk])
        self.assertRedirects(response, expected_redirect_url, status_code=302)


    def test_new_applicant_view_post_invalid_data_missing_name(self):
        """Test POSTing data with missing name re-renders form with errors."""
        initial_applicant_count = Applicant.objects.count()
        invalid_data = self.valid_post_data.copy()
        del invalid_data['name'] # Name is required

        response = self.client.post(self.new_applicant_url, invalid_data)

        self.assertEqual(response.status_code, 200) # Should re-render the form
        self.assertTemplateUsed(response, 'ats/new_applicant.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('name', response.context['form'].errors) # Check 'name' field has an error
        self.assertEqual(Applicant.objects.count(), initial_applicant_count) # No new applicant created

    def test_new_applicant_view_post_invalid_data_invalid_email(self):
        """Test POSTing data with invalid email re-renders form with errors."""
        initial_applicant_count = Applicant.objects.count()
        invalid_data = self.valid_post_data.copy()
        invalid_data['email'] = 'not-an-email' # Invalid email format

        response = self.client.post(self.new_applicant_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ats/new_applicant.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('email', response.context['form'].errors)
        self.assertEqual(Applicant.objects.count(), initial_applicant_count)


from rest_framework.test import APIClient
from rest_framework import status

class ApplicantListCreateAPIViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.list_create_url = reverse('ats:api_applicant_list')

        # Create some initial applicants for list, filter, search, order tests
        self.app1 = Applicant.objects.create(
            name="Alice Wonderland", email="alice@example.com", source="LinkedIn",
            current_stage="Submitted", tags="python, django"
        )
        self.app2 = Applicant.objects.create(
            name="Bob The Builder", email="bob@example.com", source="Indeed",
            current_stage="Under Review", tags="java, spring"
        )
        self.app3 = Applicant.objects.create(
            name="Charlie Brown", email="charlie@example.com", source="Referral",
            current_stage="Submitted", tags="python, javascript"
        )

        self.valid_payload = {
            'name': 'Derek Zoolander',
            'email': 'derek@zoolander.com',
            'source': 'Company Website',
            'current_stage': 'Technical Assessment',
            'tags': 'modelling, blue steel'
        }
        self.required_fields_payload = {
            'name': 'Hansel McDonald',
            'email': 'hansel@example.com',
            'source': 'Referral',
        }


    # List functionality (GET)
    def test_list_applicants_200_ok(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_applicants_returns_serialized_data(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(len(response.data['results']), 3) # Based on setUp and default pagination
        # Check for expected keys based on ApplicantSerializer (id, name, email, current_stage, source, tags)
        # The API returns paginated results, so access first item in 'results'
        first_applicant_data = response.data['results'][0]
        self.assertIn('id', first_applicant_data)
        self.assertIn('name', first_applicant_data)
        self.assertIn('email', first_applicant_data)
        self.assertIn('current_stage', first_applicant_data)
        self.assertIn('source', first_applicant_data)
        self.assertIn('tags', first_applicant_data)

    def test_list_applicants_empty_list(self):
        Applicant.objects.all().delete()
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['results'], [])

    # Creation functionality (POST)
    def test_create_applicant_valid_data_201_created(self):
        initial_count = Applicant.objects.count()
        response = self.client.post(self.list_create_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Applicant.objects.count(), initial_count + 1)

        # Check response data
        self.assertEqual(response.data['name'], self.valid_payload['name'])
        self.assertEqual(response.data['email'], self.valid_payload['email'])
        self.assertEqual(response.data['source'], self.valid_payload['source'])
        self.assertEqual(response.data['current_stage'], self.valid_payload['current_stage'])
        self.assertEqual(response.data['tags'], self.valid_payload['tags'])
        self.assertIn('id', response.data)

    def test_create_applicant_required_fields_only_201_created(self):
        initial_count = Applicant.objects.count()
        response = self.client.post(self.list_create_url, self.required_fields_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Applicant.objects.count(), initial_count + 1)
        created_applicant = Applicant.objects.get(email=self.required_fields_payload['email'])
        self.assertEqual(created_applicant.name, self.required_fields_payload['name'])
        self.assertEqual(created_applicant.source, self.required_fields_payload['source'])
        self.assertEqual(created_applicant.current_stage, 'Submitted') # Default value

    def test_create_applicant_invalid_data_missing_name_400_bad_request(self):
        payload = self.valid_payload.copy()
        del payload['name']
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_applicant_invalid_data_missing_email_400_bad_request(self):
        payload = self.valid_payload.copy()
        del payload['email']
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_create_applicant_invalid_data_missing_source_400_bad_request(self):
        payload = self.valid_payload.copy()
        del payload['source'] # source is required by model/serializer
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('source', response.data)

    def test_create_applicant_invalid_email_format_400_bad_request(self):
        payload = self.valid_payload.copy()
        payload['email'] = 'not-a-valid-email'
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    # Filtering (GET)
    def test_filter_applicants_by_stage(self):
        # app1: Submitted, app2: Under Review, app3: Submitted
        response = self.client.get(self.list_create_url, {'stage': 'Submitted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        for applicant in results:
            self.assertEqual(applicant['current_stage'], 'Submitted')
        names = sorted([app['name'] for app in results])
        self.assertEqual(names, sorted([self.app1.name, self.app3.name]))

        response_review = self.client.get(self.list_create_url, {'stage': 'Under Review'})
        self.assertEqual(len(response_review.data['results']), 1)
        self.assertEqual(response_review.data['results'][0]['name'], self.app2.name)

    def test_filter_applicants_by_source(self):
        # app1: LinkedIn, app2: Indeed, app3: Referral
        response = self.client.get(self.list_create_url, {'source': 'LinkedIn'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.app1.name)

        response_referral = self.client.get(self.list_create_url, {'source': 'Referral'})
        self.assertEqual(len(response_referral.data['results']), 1)
        self.assertEqual(response_referral.data['results'][0]['name'], self.app3.name)

    # Searching (GET)
    def test_search_applicants_by_name(self):
        response = self.client.get(self.list_create_url, {'search': 'Alice Wonderland'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.app1.name)

    def test_search_applicants_by_email(self):
        response = self.client.get(self.list_create_url, {'search': 'bob@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.app2.name)

    def test_search_applicants_by_tags(self):
        # app1: python, django; app3: python, javascript
        response = self.client.get(self.list_create_url, {'search': 'python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        names = sorted([app['name'] for app in results])
        self.assertEqual(names, sorted([self.app1.name, self.app3.name]))

        response_spring = self.client.get(self.list_create_url, {'search': 'spring'})
        self.assertEqual(len(response_spring.data['results']), 1)
        self.assertEqual(response_spring.data['results'][0]['name'], self.app2.name)


    # Ordering (GET)
    def test_order_applicants_by_name(self):
        response = self.client.get(self.list_create_url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 3)
        # app1 (Alice), app2 (Bob), app3 (Charlie) are already somewhat ordered by name
        self.assertEqual(results[0]['name'], self.app1.name) # Alice
        self.assertEqual(results[1]['name'], self.app2.name) # Bob
        self.assertEqual(results[2]['name'], self.app3.name) # Charlie

    def test_order_applicants_by_name_descending(self):
        response = self.client.get(self.list_create_url, {'ordering': '-name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['name'], self.app3.name) # Charlie
        self.assertEqual(results[1]['name'], self.app2.name) # Bob
        self.assertEqual(results[2]['name'], self.app1.name) # Alice

    def test_order_applicants_by_created_at_default(self):
        # Default ordering is -created_at (most recent first)
        # In setUp, app1, app2, app3 are created in that order. So app3 is latest.
        Applicant.objects.all().delete() # Clear setUp data for controlled order
        a_first = Applicant.objects.create(name="FirstCreated", email="first@example.com", source="Other")
        # Introduce a slight delay if necessary, though usually not for tests
        a_second = Applicant.objects.create(name="SecondCreated", email="second@example.com", source="Other")
        a_third = Applicant.objects.create(name="ThirdCreated", email="third@example.com", source="Other")

        response = self.client.get(self.list_create_url) # Default ordering
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['name'], "ThirdCreated")
        self.assertEqual(results[1]['name'], "SecondCreated")
        self.assertEqual(results[2]['name'], "FirstCreated")

        response_explicit = self.client.get(self.list_create_url, {'ordering': '-created_at'})
        results_explicit = response_explicit.data['results']
        self.assertEqual(results_explicit[0]['name'], "ThirdCreated")
        self.assertEqual(results_explicit[1]['name'], "SecondCreated")
        self.assertEqual(results_explicit[2]['name'], "FirstCreated")


class ApplicantDetailAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.app1 = Applicant.objects.create(
            name="Initial Name", email="initial@example.com", source="LinkedIn",
            current_stage="Submitted", tags="initial, tag"
        )
        self.detail_url = lambda pk: reverse('ats:api_applicant_detail', kwargs={'pk': pk})

        self.valid_put_payload = {
            'name': 'Updated Name PUT',
            'email': 'updated_put@example.com',
            'source': 'Indeed', # Required field
            'current_stage': 'Under Review', # Required field (or ensure serializer handles default if not provided)
            'phone': '1112223333',
            'tags': 'updated, put',
            'resume_text': 'Updated resume text for PUT.',
            'interviewers': 'Interviewer PUT',
            'interview_dates': '2024-09-01',
            'comments_ta': 'TA Comments PUT',
            'comments_initial_call': 'Initial Call Comments PUT',
            'comments_evaluation': 'Evaluation Comments PUT',
            'overall_feedback': 'Overall Feedback PUT',
            'final_decision': 'Decision PUT'
        }
        # The serializer makes most fields optional for PATCH, but core ones might be needed by model
        # For our model, name, email, source are essential. Stage has a default.
        self.valid_patch_payload = {
            'name': 'Patched Name',
            'current_stage': 'Interview Stage',
            'tags': 'patched, specific tag'
        }

    # Retrieve (GET)
    def test_retrieve_applicant_valid_id_200_ok(self):
        response = self.client.get(self.detail_url(self.app1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.app1.pk)
        self.assertEqual(response.data['name'], self.app1.name)
        self.assertEqual(response.data['email'], self.app1.email)

    def test_retrieve_applicant_invalid_id_404_not_found(self):
        response = self.client.get(self.detail_url(9999)) # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Update (PUT)
    def test_update_applicant_put_valid_data_200_ok(self):
        response = self.client.put(
            self.detail_url(self.app1.pk),
            self.valid_put_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.app1.refresh_from_db()
        self.assertEqual(self.app1.name, self.valid_put_payload['name'])
        self.assertEqual(self.app1.email, self.valid_put_payload['email'])
        self.assertEqual(self.app1.source, self.valid_put_payload['source'])
        self.assertEqual(self.app1.current_stage, self.valid_put_payload['current_stage'])
        self.assertEqual(self.app1.tags, self.valid_put_payload['tags'])
        # Check a few more fields from the payload
        self.assertEqual(self.app1.phone, self.valid_put_payload['phone'])
        self.assertEqual(self.app1.resume_text, self.valid_put_payload['resume_text'])

        # Check response data
        self.assertEqual(response.data['name'], self.valid_put_payload['name'])
        self.assertEqual(response.data['email'], self.valid_put_payload['email'])

    def test_update_applicant_put_invalid_email_400_bad_request(self):
        payload = self.valid_put_payload.copy()
        payload['email'] = 'not-a-valid-email'
        response = self.client.put(self.detail_url(self.app1.pk), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_update_applicant_put_missing_required_field_400_bad_request(self):
        # PUT requires all fields for a full update. Serializer enforces this.
        payload = self.valid_put_payload.copy()
        del payload['name'] # name is required
        response = self.client.put(self.detail_url(self.app1.pk), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update_applicant_put_non_existent_id_404_not_found(self):
        response = self.client.put(self.detail_url(9999), self.valid_put_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Partial Update (PATCH)
    def test_partial_update_applicant_patch_valid_data_200_ok(self):
        original_email = self.app1.email # Store to check it doesn't change
        response = self.client.patch(
            self.detail_url(self.app1.pk),
            self.valid_patch_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.app1.refresh_from_db()
        self.assertEqual(self.app1.name, self.valid_patch_payload['name'])
        self.assertEqual(self.app1.current_stage, self.valid_patch_payload['current_stage'])
        self.assertEqual(self.app1.tags, self.valid_patch_payload['tags'])
        self.assertEqual(self.app1.email, original_email) # Ensure other fields not changed

        # Check response data
        self.assertEqual(response.data['name'], self.valid_patch_payload['name'])
        self.assertEqual(response.data['current_stage'], self.valid_patch_payload['current_stage'])
        self.assertEqual(response.data['email'], original_email)

    def test_partial_update_applicant_patch_invalid_email_400_bad_request(self):
        payload = {'email': 'not-a-valid-email'}
        response = self.client.patch(self.detail_url(self.app1.pk), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_partial_update_applicant_patch_non_existent_id_404_not_found(self):
        response = self.client.patch(self.detail_url(9999), self.valid_patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Delete (DELETE)
    def test_delete_applicant_valid_id_204_no_content(self):
        applicant_to_delete_pk = self.app1.pk
        initial_count = Applicant.objects.count()
        response = self.client.delete(self.detail_url(applicant_to_delete_pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Applicant.objects.count(), initial_count - 1)
        with self.assertRaises(Applicant.DoesNotExist):
            Applicant.objects.get(pk=applicant_to_delete_pk)

    def test_delete_applicant_invalid_id_404_not_found(self):
        initial_count = Applicant.objects.count()
        response = self.client.delete(self.detail_url(9999)) # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Applicant.objects.count(), initial_count) # Count should not change


class ErrorPageTests(TestCase):
    @override_settings(DEBUG=False)
    def test_handler_400_renders_custom_template(self):
        response = self.client.get(reverse('ats:test_400'))
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "400", status_code=400)
        self.assertContains(response, "Bad Request", status_code=400)
        self.assertContains(response, "The server could not understand your request.", status_code=400)
        self.assertContains(response, "Back to Dashboard", status_code=400)

    @override_settings(DEBUG=False)
    def test_handler_403_renders_custom_template(self):
        response = self.client.get(reverse('ats:test_403'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "403", status_code=403)
        self.assertContains(response, "Access Forbidden", status_code=403)
        self.assertContains(response, "Sorry, you do not have permission to access this page.", status_code=403)
        self.assertContains(response, "Back to Dashboard", status_code=403)

    @override_settings(DEBUG=False)
    def test_handler_404_renders_custom_template(self):
        response = self.client.get(reverse('ats:test_404'))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)
        self.assertContains(response, "Page Not Found", status_code=404)
        self.assertContains(response, "The page you are looking for might have been removed", status_code=404)
        self.assertContains(response, "Back to Dashboard", status_code=404)

    @override_settings(DEBUG=False)
    def test_handler_500_renders_custom_template(self):
        response = self.client.get(reverse('ats:test_500'))
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "500", status_code=500)
        self.assertContains(response, "Internal Server Error", status_code=500)
        self.assertContains(response, "We are currently experiencing technical difficulties.", status_code=500)
        self.assertContains(response, "Back to Dashboard", status_code=500)
