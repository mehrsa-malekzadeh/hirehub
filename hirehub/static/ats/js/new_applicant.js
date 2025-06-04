// API Configuration
const API_BASE_URL = '/api/applicants/';

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Add form validation
    const form = document.getElementById('newApplicantForm');
    form.addEventListener('submit', createApplicant);
});

// Create new applicant
async function createApplicant(event) {
    event.preventDefault();
    
    hideMessages();
    
    const formData = new FormData(event.target);
    
    // Prepare data for API
    const applicantData = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        source: formData.get('source'),
        tags: formData.get('tags'),
        current_stage: 'Submitted' // Default stage for new applicants
    };
    
    // Handle file upload if present
    const resumeFile = formData.get('resume_file');
    
    try {
        let response;
        
        if (resumeFile && resumeFile.size > 0) {
            // If there's a file, use FormData for multipart upload
            const uploadData = new FormData();
            Object.keys(applicantData).forEach(key => {
                uploadData.append(key, applicantData[key]);
            });
            uploadData.append('resume_file', resumeFile);
            
            response = await fetch(API_BASE_URL, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                },
                body: uploadData
            });
        } else {
            // No file, use JSON
            response = await fetch(API_BASE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(applicantData)
            });
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(formatApiErrors(errorData));
        }
        
        const newApplicant = await response.json();
        
        showSuccess('Applicant created successfully!');
        
        // Reset form
        event.target.reset();
        
        // Redirect to applicant details after a short delay
        setTimeout(() => {
            window.location.href = `/ats/applicant/${newApplicant.applicant_id || newApplicant.id}/`;
        }, 2000);
        
    } catch (error) {
        console.error('Error creating applicant:', error);
        showError('Failed to create applicant: ' + error.message);
    }
}

// Format API errors for display
function formatApiErrors(errorData) {
    if (typeof errorData === 'string') {
        return errorData;
    }
    
    if (errorData.detail) {
        return errorData.detail;
    }
    
    // Handle field-specific errors
    const errors = [];
    for (const [field, messages] of Object.entries(errorData)) {
        if (Array.isArray(messages)) {
            errors.push(`${field}: ${messages.join(', ')}`);
        } else {
            errors.push(`${field}: ${messages}`);
        }
    }
    
    return errors.length > 0 ? errors.join('\n') : 'Unknown error occurred';
}

// Utility functions
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

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('newApplicantForm');
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
});

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Remove existing error styling
    field.classList.remove('error');
    
    // Basic validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    return true;
}

function showFieldError(field, message) {
    field.classList.add('error');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#c62828';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '5px';
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('error');
    
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}
