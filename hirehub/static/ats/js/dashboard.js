// Global variables
let applicantsData = [];
let filteredData = [];
let currentSort = { field: null, direction: 'asc' };
let currentPage = 1;
const itemsPerPage = 20;

// API Configuration
const API_BASE_URL = '/api/applicants/';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Try to load data from Django context first
    if (typeof initialApplicantsData !== 'undefined' && initialApplicantsData !== null && initialApplicantsData.length > 0) {
        console.log("Loading data from Django context");
        applicantsData = initialApplicantsData;
        filteredData = [...applicantsData];

        // Apply initial filters from server-rendered values
        if (typeof initialFilters !== 'undefined') {
            document.getElementById('searchInput').value = initialFilters.search || '';
            document.getElementById('stageFilter').value = initialFilters.stage || '';
            document.getElementById('sourceFilter').value = initialFilters.source || '';
            // Call applyFilters to ensure the view is consistent with initial filter values
            applyFilters(initialFilters.search);
        } else {
            applyFilters(); // Apply default empty filters if initialFilters is not defined
        }

        renderTable();
        renderPagination();
        showLoading(false); // Hide loading spinner as data is already loaded
    } else {
        // If no initial data, or it's empty, load from API as fallback or for subsequent loads
        console.log("Initial data not found or empty, loading from API");
        loadApplicants();
    }

    // Event listener for search input Enter key
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchApplicants();
            }
        });
    }
});

// Load applicants from API (used as fallback or for refresh functionality if added later)
async function loadApplicants() {
    showLoading(true);
    hideError();
    
    try {
        const response = await fetch(API_BASE_URL); // Fetches all applicants
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        // Assuming API returns a list directly, or a paginated response with a 'results' field
        applicantsData = data.results || data;
        filteredData = [...applicantsData]; // Initialize filteredData with all applicants
        
        // Apply filters that might be set in the UI (e.g., if user types before API loads)
        // This ensures consistency if API load is slow and user interacts with filters.
        const currentSearchTerm = document.getElementById('searchInput').value;
        applyFilters(currentSearchTerm); // This will also call renderTable and renderPagination

    } catch (error) {
        console.error('Error loading applicants from API:', error);
        showError('Failed to load applicants. Please try again.');
        applicantsData = []; // Ensure data is empty on error
        filteredData = [];
        renderTable(); // Render empty table
        renderPagination(); // Render empty pagination
    } finally {
        showLoading(false);
    }
}

// Render applicants table
function renderTable() {
    const tbody = document.getElementById('applicantsTableBody');
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = filteredData.slice(startIndex, endIndex);
    
    if (pageData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px;">No applicants found</td></tr>';
        return;
    }
    
    tbody.innerHTML = pageData.map(applicant => `
        <tr>
            <td>${applicant.applicant_id || applicant.id}</td>
            <td>${escapeHtml(applicant.name)}</td>
            <td>${escapeHtml(applicant.email)}</td>
            <td><span class="status-badge ${getStatusClass(applicant.current_stage)}">${escapeHtml(applicant.current_stage)}</span></td>
            <td>${escapeHtml(applicant.source || 'N/A')}</td>
            <td>${formatDate(applicant.last_status_update || applicant.updated_at)}</td>
            <td>
                <button onclick="viewApplicant(${applicant.applicant_id || applicant.id})" class="btn btn-primary" style="font-size: 12px; padding: 6px 12px;">
                    View Details
                </button>
            </td>
        </tr>
    `).join('');
}

// Render pagination
function renderPagination() {
    const pagination = document.getElementById('pagination');
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `<button onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Previous</button>`;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            paginationHTML += `<button onclick="changePage(${i})" ${i === currentPage ? 'class="active"' : ''}>${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            paginationHTML += '<span>...</span>';
        }
    }
    
    // Next button
    paginationHTML += `<button onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>`;
    
    pagination.innerHTML = paginationHTML;
}

// Change page
function changePage(page) {
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        renderTable();
        renderPagination();
    }
}

// Sort table
function sortTable(field) {
    if (currentSort.field === field) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = field;
        currentSort.direction = 'asc';
    }
    
    filteredData.sort((a, b) => {
        let aVal = a[field] || '';
        let bVal = b[field] || '';
        
        // Handle different data types
        if (field === 'applicant_id' || field === 'id') {
            aVal = parseInt(aVal) || 0;
            bVal = parseInt(bVal) || 0;
        } else if (field === 'last_status_update' || field === 'updated_at') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        } else {
            aVal = aVal.toString().toLowerCase();
            bVal = bVal.toString().toLowerCase();
        }
        
        if (aVal < bVal) return currentSort.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
    });
    
    currentPage = 1;
    renderTable();
    renderPagination();
    updateSortArrows();
}

// Update sort arrows
function updateSortArrows() {
    document.querySelectorAll('.sort-arrow').forEach(arrow => {
        arrow.textContent = '↕';
    });
    
    if (currentSort.field) {
        const header = document.querySelector(`th[onclick="sortTable('${currentSort.field}')"] .sort-arrow`);
        if (header) {
            header.textContent = currentSort.direction === 'asc' ? '↑' : '↓';
        }
    }
}

// Search applicants
function searchApplicants() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    applyFilters(searchTerm);
}

// Filter applicants
function filterApplicants() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    applyFilters(searchTerm);
}

// Apply all filters
function applyFilters(searchTerm = '') {
    const stageFilter = document.getElementById('stageFilter').value;
    const sourceFilter = document.getElementById('sourceFilter').value;
    
    filteredData = applicantsData.filter(applicant => {
        const matchesSearch = !searchTerm || 
            applicant.name.toLowerCase().includes(searchTerm) ||
            applicant.email.toLowerCase().includes(searchTerm) ||
            (applicant.tags && applicant.tags.toLowerCase().includes(searchTerm));
        
        const matchesStage = !stageFilter || applicant.current_stage === stageFilter;
        const matchesSource = !sourceFilter || applicant.source === sourceFilter;
        
        return matchesSearch && matchesStage && matchesSource;
    });
    
    currentPage = 1;
    renderTable();
    renderPagination();
}

// Clear filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('stageFilter').value = '';
    document.getElementById('sourceFilter').value = '';
    filteredData = [...applicantsData];
    currentPage = 1;
    renderTable();
    renderPagination();
}

// View applicant details
function viewApplicant(id) {
    window.location.href = `/ats/applicant/${id}/`;
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function getStatusClass(status) {
    if (!status) return '';
    return 'status-' + status.toLowerCase().replace(/\s+/g, '-');
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
}

function hideError() {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.classList.add('hidden');
}

// Note: The DOMContentLoaded listener for search input was moved to the main DOMContentLoaded
// to avoid re-registering if this script is somehow loaded multiple times or for cleaner organization.
