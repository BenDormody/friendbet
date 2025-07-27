// Base JavaScript for Fantasy Betting League

document.addEventListener('DOMContentLoaded', function() {
    setupFormHandlers();
    setupModalHandlers();
    initializeTooltips();
    checkAuthStatus();
});

// Authentication State Management
let currentUser = null;

// Check authentication status on page load
async function checkAuthStatus() {
    try {
        const response = await FantasyBetting.API.get('/api/auth/check');
        if (response.authenticated) {
            currentUser = response.user;
            updateUIForAuthenticatedUser();
        } else {
            updateUIForUnauthenticatedUser();
        }
    } catch (error) {
        console.log('User not authenticated');
        updateUIForUnauthenticatedUser();
    }
}

function updateUIForAuthenticatedUser() {
    // Update navigation
    const authButtons = document.querySelector('.d-flex.gap-2');
    if (authButtons && currentUser) {
        authButtons.innerHTML = `
            <span class="text-secondary me-3">Welcome, ${currentUser.username}!</span>
            <button class="btn btn-secondary-custom" onclick="FantasyBetting.logout()">Logout</button>
        `;
    }
}

function updateUIForUnauthenticatedUser() {
    // Update navigation
    const authButtons = document.querySelector('.d-flex.gap-2');
    if (authButtons) {
        authButtons.innerHTML = `
            <button class="btn btn-secondary-custom" onclick="FantasyBetting.showLoginModal()">Login</button>
            <button class="btn btn-primary-custom" onclick="FantasyBetting.showRegisterModal()">Sign Up</button>
        `;
    }
}

// Modal Management Functions
function showLoginModal() {
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
}

function showRegisterModal() {
    const modal = new bootstrap.Modal(document.getElementById('registerModal'));
    modal.show();
}

function showCreateLeagueModal() {
    if (!currentUser) {
        showAlert('Please log in to create a league', 'warning');
        showLoginModal();
        return;
    }
    const modal = new bootstrap.Modal(document.getElementById('createLeagueModal'));
    modal.show();
}

function showJoinLeagueModal() {
    if (!currentUser) {
        showAlert('Please log in to join a league', 'warning');
        showLoginModal();
        return;
    }
    const modal = new bootstrap.Modal(document.getElementById('joinLeagueModal'));
    modal.show();
}

// Form Handlers
function setupFormHandlers() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            try {
                showLoading(submitBtn);
                
                const response = await FantasyBetting.API.post('/api/auth/login', {
                    email: email,
                    password: password
                });
                
                currentUser = response.user;
                showAlert(response.message, 'success');
                updateUIForAuthenticatedUser();
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
                modal.hide();
                
            } catch (error) {
                console.error('Login error:', error);
                const errorMessage = error.message || 'Login failed. Please try again.';
                showAlert(errorMessage, 'danger');
            } finally {
                hideLoading(submitBtn, originalText);
            }
        });
    }

    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('registerUsername').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            try {
                showLoading(submitBtn);
                
                const response = await FantasyBetting.API.post('/api/auth/register', {
                    username: username,
                    email: email,
                    password: password
                });
                
                showAlert(response.message, 'success');
                
                // Close modal and show login modal
                const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
                registerModal.hide();
                
                // Show login modal
                setTimeout(() => {
                    showLoginModal();
                }, 1000);
                
            } catch (error) {
                console.error('Registration error:', error);
                const errorMessage = error.message || 'Registration failed. Please try again.';
                showAlert(errorMessage, 'danger');
            } finally {
                hideLoading(submitBtn, originalText);
            }
        });
    }

    // Create league form
    const createLeagueForm = document.getElementById('createLeagueForm');
    if (createLeagueForm) {
        createLeagueForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('leagueName').value;
            const description = document.getElementById('leagueDescription').value;
            const startingBalance = document.getElementById('startingBalance').value;
            
            // TODO: Implement actual league creation logic
            console.log('Create league attempt:', { name, description, startingBalance });
            showAlert('League creation functionality will be implemented with backend integration', 'info');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createLeagueModal'));
            modal.hide();
        });
    }

    // Join league form
    const joinLeagueForm = document.getElementById('joinLeagueForm');
    if (joinLeagueForm) {
        joinLeagueForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const inviteCode = document.getElementById('inviteCode').value;
            
            // TODO: Implement actual join league logic
            console.log('Join league attempt:', { inviteCode });
            showAlert('Join league functionality will be implemented with backend integration', 'info');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('joinLeagueModal'));
            modal.hide();
        });
    }
}

// Modal Event Handlers
function setupModalHandlers() {
    // Clear form data when modals are hidden
    const modals = ['loginModal', 'registerModal', 'createLeagueModal', 'joinLeagueModal'];
    
    modals.forEach(modalId => {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            modalElement.addEventListener('hidden.bs.modal', function() {
                const form = this.querySelector('form');
                if (form) {
                    form.reset();
                }
            });
        }
    });
}

// Logout function
async function logout() {
    try {
        await FantasyBetting.API.post('/api/auth/logout');
        currentUser = null;
        showAlert('Logout successful!', 'success');
        updateUIForUnauthenticatedUser();
    } catch (error) {
        console.error('Logout error:', error);
        showAlert('Logout failed. Please try again.', 'danger');
    }
}

// Utility Functions
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 5rem; right: 1rem; z-index: 9999; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// API Helper Functions
class API {
    static async get(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    }

    static async post(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const responseData = await response.json();
            
            if (!response.ok) {
                throw new Error(responseData.error || `HTTP error! status: ${response.status}`);
            }
            
            return responseData;
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    }
}

// Navigation Helper
function navigateTo(url) {
    window.location.href = url;
}

// League Management Functions
function openLeague(leagueId) {
    if (!currentUser) {
        showAlert('Please log in to view leagues', 'warning');
        showLoginModal();
        return;
    }
    // TODO: Navigate to league detail page
    console.log('Opening league:', leagueId);
    showAlert(`League detail page for league ${leagueId} will be implemented`, 'info');
}

// Loading State Management
function showLoading(element) {
    if (element) {
        element.disabled = true;
        element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    }
}

function hideLoading(element, originalText) {
    if (element) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
}

// Form Validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(function (field) {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function () {
        showAlert('Copied to clipboard!', 'success');
    }).catch(function (err) {
        console.error('Could not copy text: ', err);
        showAlert('Failed to copy to clipboard', 'danger');
    });
}

// Export functions for use in other scripts
window.FantasyBetting = {
    showLoginModal,
    showRegisterModal,
    showCreateLeagueModal,
    showJoinLeagueModal,
    showAlert,
    formatCurrency,
    formatDate,
    openLeague,
    navigateTo,
    showLoading,
    hideLoading,
    validateForm,
    copyToClipboard,
    logout,
    API,
    currentUser: () => currentUser
}; 