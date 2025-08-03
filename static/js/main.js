// Main JavaScript for Gestão de Atividades

document.addEventListener('DOMContentLoaded', function() {
    console.log('Gestão de Atividades - Sistema carregado');
    
    // Initialize components
    initializeTooltips();
    initializeWordCounters();
    initializeFormValidation();
    initializeCardAnimations();
    initializeNavigation();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(hideAlerts, 5000);
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize word counters for form fields
 */
function initializeWordCounters() {
    const wordCountFields = document.querySelectorAll('[data-word-limit]');
    
    wordCountFields.forEach(field => {
        const limit = parseInt(field.getAttribute('data-word-limit'));
        const counterId = field.id + '-counter';
        let counter = document.getElementById(counterId);
        
        if (!counter) {
            counter = document.createElement('div');
            counter.id = counterId;
            counter.className = 'form-text';
            field.parentNode.appendChild(counter);
        }
        
        function updateCounter() {
            const words = field.value.trim().split(/\s+/).filter(word => word.length > 0);
            const wordCount = field.value.trim() === '' ? 0 : words.length;
            
            counter.textContent = `${wordCount}/${limit} palavras`;
            
            if (wordCount > limit) {
                counter.classList.add('text-danger');
                field.classList.add('is-invalid');
            } else {
                counter.classList.remove('text-danger');
                field.classList.remove('is-invalid');
            }
        }
        
        field.addEventListener('input', updateCounter);
        updateCounter(); // Initialize
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Validate form fields
 */
function validateForm(form) {
    let isValid = true;
    
    // Check required fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // Check word limits
    const wordLimitFields = form.querySelectorAll('[data-word-limit]');
    wordLimitFields.forEach(field => {
        const limit = parseInt(field.getAttribute('data-word-limit'));
        const words = field.value.trim().split(/\s+/).filter(word => word.length > 0);
        const wordCount = field.value.trim() === '' ? 0 : words.length;
        
        if (wordCount > limit) {
            isValid = false;
            field.classList.add('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Initialize card animations
 */
function initializeCardAnimations() {
    const cards = document.querySelectorAll('.card');
    
    // Add fade-in animation to cards
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add hover effects to activity cards
    const activityCards = document.querySelectorAll('.activity-card');
    activityCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Initialize navigation features
 */
function initializeNavigation() {
    // Auto-collapse navbar on mobile after clicking a link
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    if (navbarToggler && navbarCollapse) {
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                }
            });
        });
    }
    
    // Highlight current page in navigation
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Hide alert messages automatically
 */
function hideAlerts() {
    const alerts = document.querySelectorAll('.alert[data-auto-hide="true"], .alert:not([data-auto-hide="false"])');
    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}

/**
 * Show loading spinner
 */
function showLoading(button) {
    if (button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Carregando...';
        button.disabled = true;
        
        // Restore original text after 3 seconds (fallback)
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 3000);
    }
}

/**
 * Hide loading spinner
 */
function hideLoading(button) {
    if (button && button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * Format datetime for display
 */
function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show confirmation dialog
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        if (typeof callback === 'function') {
            callback();
        }
        return true;
    }
    return false;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Create toast element
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

/**
 * Mobile-specific optimizations
 */
function initializeMobileOptimizations() {
    // Improve touch interactions on mobile
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Add touch feedback to buttons
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.classList.add('active');
            });
            
            button.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('active');
                }, 150);
            });
        });
    }
    
    // Optimize for viewport changes
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Recalculate any layout-dependent features
            initializeCardAnimations();
        }, 250);
    });
}

// Initialize mobile optimizations
initializeMobileOptimizations();

// Global error handler
window.addEventListener('error', function(event) {
    console.error('JavaScript Error:', event.error);
    // You could send this to a logging service in production
});

// Utility functions for external use
window.ActivityManager = {
    showLoading,
    hideLoading,
    formatDate,
    formatDateTime,
    confirmAction,
    showToast,
    validateForm
};
