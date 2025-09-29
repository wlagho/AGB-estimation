// Authentication related JavaScript functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize password strength checker
    initializePasswordStrength();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Toggle password visibility
function togglePassword() {
    const passwordField = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleIcon.className = 'fas fa-eye-slash';
    } else {
        passwordField.type = 'password';
        toggleIcon.className = 'fas fa-eye';
    }
}

// Toggle confirm password visibility
function togglePassword2() {
    const passwordField = document.getElementById('password2');
    const toggleIcon = document.getElementById('toggleIcon2');
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleIcon.className = 'fas fa-eye-slash';
    } else {
        passwordField.type = 'password';
        toggleIcon.className = 'fas fa-eye';
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Password strength checker
function initializePasswordStrength() {
    const passwordField = document.getElementById('password');
    if (!passwordField) return;
    
    passwordField.addEventListener('input', function() {
        const password = this.value;
        const strength = checkPasswordStrength(password);
        updatePasswordStrengthIndicator(strength);
    });
}

function checkPasswordStrength(password) {
    let score = 0;
    
    // Length check
    if (password.length >= 8) score += 1;
    
    // Uppercase check
    if (/[A-Z]/.test(password)) score += 1;
    
    // Lowercase check
    if (/[a-z]/.test(password)) score += 1;
    
    // Number check
    if (/\d/.test(password)) score += 1;
    
    // Special character check
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1;
    
    if (score < 3) return 'weak';
    if (score < 5) return 'medium';
    return 'strong';
}

function updatePasswordStrengthIndicator(strength) {
    let indicator = document.querySelector('.password-strength');
    
    // Create indicator if it doesn't exist
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'password-strength';
        
        const passwordField = document.getElementById('password');
        passwordField.parentNode.insertBefore(indicator, passwordField.nextSibling);
    }
    
    // Update indicator
    indicator.className = `password-strength strength-${strength}`;
}

// Auto-dismiss alerts after 5 seconds
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// Form loading states
function setFormLoading(formElement, loading = true) {
    const submitButton = formElement.querySelector('button[type="submit"]');
    const inputs = formElement.querySelectorAll('input, select, textarea');
    
    if (loading) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        inputs.forEach(input => input.disabled = true);
    } else {
        submitButton.disabled = false;
        submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
        inputs.forEach(input => input.disabled = false);
    }
}