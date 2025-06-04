// Global variables
let applicantId = null;
let applicantData = null;

// API Configuration
const API_BASE_URL = '/api/applicants/';

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Extract applicant ID from URL
    const pathParts = window.location.pathname.split('/');
    applicantId = pathParts[pathParts.length - 2]; // Assuming URL like /ats/applicant/123/
    
    if (applicantId) {
        loadApplicantDetails();
    } else {
        showError('Invalid applicant ID');
    }
});

// Load applicant details from API
async function loadApplicantDetails() {
    showLoading(true);
    hideMessages();
    
    try {
        const response = await fetch(`${API_BASE_URL}${applicantId}/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        applicantData = await response.json();
        populateApplicantDetails();
        
    } catch (error) {
        console.error('Error loading applicant details:', error);
        showError('Failed to load applicant details. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Populate applicant details in the form
function populateApplicantDetails() {
    if (!applicantData) return;
    
    // Basic Information
    document.getElementById('applicantId').textContent = applicantData.applicant_id || applicantData.id;
    document.getElementById('applicantName').textContent = applicantData.name;
    document.getElementById('applicantNameField').textContent = applicantData.name;
    document.getElementById('applicantEmail').textContent = applicantData.email;
    document.getElementById('applicantPhone').textContent = applicantData.phone || 'N/A';
    document.getElementById('applicantSource').textContent = applicantData.source || 'N/A';
    document.getElementById('applicantCreated').textContent = formatDate(applicantData.created_at);
    
    // Current Stage
    document.getElementById('currentStage').value = applicantData.current_stage || 'Submitted';
    
    // Resume Information
    if (applicantData.resume_file) {
        document.getElementById('noResumeFile').classList.add('hidden');
        const resumeLink = document.getElementById('resumeFileLink');
        resumeLink.href = applicantData.resume_file;
        resumeLink.classList.remove('hidden');
    }
    
    if (applicantData.resume_text) {
        document.getElementById('noResumeText').classList.add('hidden');
        document.getElementById('resumeText').textContent = applicantData.resume_text;
        document.getElementById('resumeText').classList.remove('hidden');
    }
    
    // Tags
    populateTags(applicantData.tags);
    
    // Interview Information
    document.getElementById('interviewers').textContent = applicantData.interviewers || 'N/A';
    document.getElementById('interviewDates').textContent = formatInterviewDates(applicantData.interview_dates);
    
    // Comments
    document.getElementById('commentsTA').value = applicantData.comments_ta || '';
    document.getElementById('commentsInitialCall').value = applicantData.comments_initial_call || '';
    document.getElementById('commentsEvaluation').value = applicantData.comments_evaluation || '';
    
    // Final Assessment
    document.getElementById('overallFeedback').textContent = applicantData.overall_feedback || 'N/A';
    document.getElementById('finalDecision').textContent = applicantData.final_decision || 'N/A';
    
    // Show the details section
    document.getElementById('applicantDetails').classList.remove('hidden');
}

// Populate tags
function populateTags(tags) {
    const container = document.getElementById('tagsContainer');
    
    if (!tags) {
        container.innerHTML = '<span class="readonly-field">No tags</span>';
        return;
    }
    
    const tagList = typeof tags === 'string' ? tags.split(',') : tags;
    container.innerHTML = tagList.map(tag => 
        `<span class="tag">${escapeHtml(tag.trim())}</span>`
    ).join('');
}

// Format interview dates
function formatInterviewDates(dates) {
    if (!dates) return 'N/A';
    
    if (typeof dates === 'string') {
        try {
            const dateList = JSON.parse(dates);
            return dateList.map(date => formatDate(date)).join(', ');
        } catch (e) {
            return dates;
        }
    }
    
    if (Array.isArray(dates)) {
        return dates.map(date => formatDate(date)).join(', ');
    }
    
    return formatDate(dates);
}

// Update applicant
async function updateApplicant(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const updateData = {
        current_stage: formData.get('current_stage'),
        comments_ta: formData.get('comments_ta'),
        comments_initial_call: formData.get('comments_initial_call'),
        comments_evaluation: formData.get('comments_evaluation')
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${applicantId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(updateData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const updatedData = await response.json();
        applicantData = updatedData;
        
        showSuccess('Applicant updated successfully!');
        
        // Optionally reload the data to ensure consistency
        setTimeout(() => {
            loadApplicantDetails();
        }, 1000);
        
    } catch (error) {
        console.error('Error updating applicant:', error);
        showError('Failed to update applicant: ' + error.message);
    }
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    // Scroll to top to show error
    window.scrollTo(0, 0);
}

function showSuccess(message) {
    const successDiv = document.getElementById('successMessage');
    successDiv.textContent = message;
    successDiv.classList.remove('hidden');
    
    // Hide after 5 seconds
    setTimeout(() => {
        successDiv.classList.add('hidden');
    }, 5000);
    
    // Scroll to top to show success
    window.scrollTo(0, 0);
}

function hideMessages() {
    document.getElementById('errorMessage').classList.add('hidden');
    document.getElementById('successMessage').classList.add('hidden');
}

function getCsrfToken() {
    // Get CSRF token from Django
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        return csrfToken.value;
    }
    
    // Alternative: get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    return '';
}
