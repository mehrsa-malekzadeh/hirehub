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
    console.log('DOMContentLoaded event fired.');
    let localInitialApplicantsData = []; // Use a local variable, then assign to global if valid

    // Safely parse initialApplicantsData from rawJsonData (defined in HTML script tag)
    if (typeof rawJsonData !== 'undefined' && rawJsonData) {
        try {
            localInitialApplicantsData = JSON.parse(rawJsonData);
        } catch (e) {
            console.error("Error parsing rawJsonData:", e, "Raw data was:", rawJsonData);
            // localInitialApplicantsData remains []
        }
    }

    console.log('Checking parsed initialApplicantsData within DOMContentLoaded:');
    // Check localInitialApplicantsData instead of the global one that might not be set yet
    if (localInitialApplicantsData && typeof localInitialApplicantsData.slice === 'function') { // Check if it's array-like
        console.log('Parsed initialApplicantsData (first 2 items) in JS:', localInitialApplicantsData.slice(0, 2));
        console.log('Type of parsed initialApplicantsData in JS:', typeof localInitialApplicantsData);
        console.log('Is parsed initialApplicantsData an Array in JS?', Array.isArray(localInitialApplicantsData));
        console.log('Length of parsed initialApplicantsData in JS:', localInitialApplicantsData.length);
    } else {
        console.error('Parsed initialApplicantsData is not an array or is undefined in dashboard.js DOMContentLoaded!');
    }

    // Try to load data from Django context first
    // Use the locally parsed and validated localInitialApplicantsData
    if (Array.isArray(localInitialApplicantsData) && localInitialApplicantsData.length > 0) {
        console.log("Loading data from successfully parsed Django context");
        applicantsData = localInitialApplicantsData; // Assign to global
        filteredData = [...applicantsData]; // Assign to global

        // Apply initial filters from server-rendered values
        if (typeof initialFilters !== 'undefined') {
            document.getElementById('searchInput').value = initialFilters.search || '';
            document.getElementById('stageFilter').value = initialFilters.stage || '';
            document.getElementById('sourceFilter').value = initialFilters.source || '';
            applyFilters(initialFilters.search);
        } else {
            applyFilters();
        }

        renderTable();
        renderPagination();
        showLoading(false);
    } else {
        console.log('Parsed initialApplicantsData is empty or invalid. Falling back to loadApplicants().');
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
        let rawData = []; // Initialize as empty array

        if (data && typeof data === 'object') {
            if (Array.isArray(data.results)) {
                rawData = data.results; // Handle DRF paginated response
            } else if (Array.isArray(data)) {
                rawData = data; // Handle non-paginated list response
            } else {
                // Log if the structure is an object but not as expected
                console.error('API response is an object but not in expected format (array or {results: array}):', data);
            }
        } else {
            // Log if the response is not even an object (e.g., null, string, number)
            console.error('API response is not a valid object or array:', data);
        }

        applicantsData = rawData; // Ensure applicantsData is always at least []
        filteredData = [...applicantsData]; // Create a new array for filtering
        
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

    console.log('renderTable called. Page data (first 2 items):', pageData.slice(0,2));
    console.log('filteredData length:', filteredData.length);
    console.log('currentPage:', currentPage);
    console.log('itemsPerPage:', itemsPerPage);
    
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
