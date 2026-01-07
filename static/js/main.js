/**
 * Xpert Farmer IMS - Main JavaScript File
 * Contains core functionality for the application
 */

// Document Ready Function
document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
    setupEventListeners();
    loadUserPreferences();
});

/**
 * Initialize the application
 */
function initializeApplication() {
    console.log('Xpert Farmer IMS Application Initialized');
    
    // Set current year in footer
    setCurrentYear();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Check for active notifications
    checkNotifications();
    
    // Set up auto-save for forms
    setupAutoSave();
    
    // Initialize theme based on user preference
    initializeTheme();
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Navigation toggle for mobile
    const sidebarToggle = document.querySelector('[data-bs-toggle="sidebar"]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Table row selection
    document.querySelectorAll('.select-row').forEach(checkbox => {
        checkbox.addEventListener('change', handleRowSelection);
    });
    
    // Select all checkbox
    const selectAllCheckbox = document.querySelector('.select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', handleSelectAll);
    }
    
    // Bulk actions
    const bulkActionSelect = document.querySelector('.bulk-action-select');
    if (bulkActionSelect) {
        bulkActionSelect.addEventListener('change', handleBulkAction);
    }
    
    // Print buttons
    document.querySelectorAll('.btn-print').forEach(btn => {
        btn.addEventListener('click', handlePrint);
    });
    
    // Export buttons
    document.querySelectorAll('.btn-export').forEach(btn => {
        btn.addEventListener('click', handleExport);
    });
    
    // Modal form submissions
    document.querySelectorAll('.modal-form').forEach(form => {
        form.addEventListener('submit', handleModalSubmit);
    });
    
    // File upload preview
    document.querySelectorAll('.file-upload').forEach(input => {
        input.addEventListener('change', previewUploadedFile);
    });
    
    // Auto-refresh for dashboard
    if (document.querySelector('.dashboard-container')) {
        setupDashboardAutoRefresh();
    }
}

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover'
        });
    });
    
    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        }).show();
    });
}

/**
 * Set current year in footer
 */
function setCurrentYear() {
    const yearElements = document.querySelectorAll('.current-year');
    const currentYear = new Date().getFullYear();
    
    yearElements.forEach(element => {
        element.textContent = currentYear;
    });
}

/**
 * Toggle sidebar on mobile
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
        
        // Store sidebar state
        const isOpen = sidebar.classList.contains('show');
        localStorage.setItem('sidebarOpen', isOpen);
    }
}

/**
 * Handle search functionality
 * @param {Event} event - Input event
 */
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase().trim();
    const searchType = event.target.dataset.searchType || 'all';
    
    if (searchTerm.length < 2) {
        resetSearch();
        return;
    }
    
    // Show loading state
    showLoading('Searching...');
    
    // Perform search based on type
    switch(searchType) {
        case 'farms':
            searchFarms(searchTerm);
            break;
        case 'farmers':
            searchFarmers(searchTerm);
            break;
        case 'reports':
            searchReports(searchTerm);
            break;
        default:
            searchAll(searchTerm);
    }
    
    // Hide loading after delay
    setTimeout(() => hideLoading(), 500);
}

/**
 * Search farms
 * @param {string} term - Search term
 */
function searchFarms(term) {
    console.log(`Searching farms for: ${term}`);
    // Implement farm search logic
}

/**
 * Search farmers
 * @param {string} term - Search term
 */
function searchFarmers(term) {
    console.log(`Searching farmers for: ${term}`);
    // Implement farmer search logic
}

/**
 * Search reports
 * @param {string} term - Search term
 */
function searchReports(term) {
    console.log(`Searching reports for: ${term}`);
    // Implement report search logic
}

/**
 * Search all content
 * @param {string} term - Search term
 */
function searchAll(term) {
    console.log(`Searching all for: ${term}`);
    // Implement global search logic
}

/**
 * Reset search results
 */
function resetSearch() {
    const searchResults = document.querySelector('.search-results');
    if (searchResults) {
        searchResults.innerHTML = '';
        searchResults.classList.remove('show');
    }
}

/**
 * Handle table row selection
 * @param {Event} event - Change event
 */
function handleRowSelection(event) {
    const checkbox = event.target;
    const row = checkbox.closest('tr');
    const selectedRows = document.querySelectorAll('.select-row:checked');
    
    if (row) {
        if (checkbox.checked) {
            row.classList.add('table-active');
        } else {
            row.classList.remove('table-active');
        }
    }
    
    // Update bulk action button state
    updateBulkActionState(selectedRows.length);
    
    // Update select all checkbox
    updateSelectAllCheckbox(selectedRows.length);
}

/**
 * Handle select all checkbox
 * @param {Event} event - Change event
 */
function handleSelectAll(event) {
    const checkAll = event.target.checked;
    const checkboxes = document.querySelectorAll('.select-row');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = checkAll;
        const row = checkbox.closest('tr');
        if (row) {
            if (checkAll) {
                row.classList.add('table-active');
            } else {
                row.classList.remove('table-active');
            }
        }
    });
    
    // Update bulk action button state
    updateBulkActionState(checkAll ? checkboxes.length : 0);
}

/**
 * Update bulk action button state
 * @param {number} selectedCount - Number of selected rows
 */
function updateBulkActionState(selectedCount) {
    const bulkActionBtn = document.querySelector('.bulk-action-btn');
    if (bulkActionBtn) {
        if (selectedCount > 0) {
            bulkActionBtn.disabled = false;
            bulkActionBtn.textContent = `Apply to ${selectedCount} item${selectedCount !== 1 ? 's' : ''}`;
        } else {
            bulkActionBtn.disabled = true;
            bulkActionBtn.textContent = 'Bulk Actions';
        }
    }
}

/**
 * Update select all checkbox
 * @param {number} selectedCount - Number of selected rows
 */
function updateSelectAllCheckbox(selectedCount) {
    const selectAllCheckbox = document.querySelector('.select-all');
    const totalRows = document.querySelectorAll('.select-row').length;
    
    if (selectAllCheckbox && totalRows > 0) {
        if (selectedCount === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedCount === totalRows) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }
}

/**
 * Handle bulk actions
 * @param {Event} event - Change event
 */
function handleBulkAction(event) {
    const action = event.target.value;
    const selectedRows = document.querySelectorAll('.select-row:checked');
    
    if (selectedRows.length === 0) {
        showToast('Please select at least one item', 'warning');
        event.target.value = '';
        return;
    }
    
    if (action) {
        const selectedIds = Array.from(selectedRows).map(checkbox => checkbox.value);
        
        switch(action) {
            case 'delete':
                confirmBulkDelete(selectedIds);
                break;
            case 'export':
                exportSelected(selectedIds);
                break;
            case 'activate':
                updateStatus(selectedIds, 'active');
                break;
            case 'deactivate':
                updateStatus(selectedIds, 'inactive');
                break;
            default:
                console.log(`Bulk action: ${action}`, selectedIds);
        }
        
        // Reset select
        event.target.value = '';
    }
}

/**
 * Confirm bulk delete
 * @param {Array} ids - Array of IDs to delete
 */
function confirmBulkDelete(ids) {
    const count = ids.length;
    const itemText = count === 1 ? 'item' : 'items';
    
    if (confirm(`Are you sure you want to delete ${count} ${itemText}? This action cannot be undone.`)) {
        performBulkDelete(ids);
    }
}

/**
 * Perform bulk delete
 * @param {Array} ids - Array of IDs to delete
 */
function performBulkDelete(ids) {
    showLoading(`Deleting ${ids.length} items...`);
    
    // Simulate API call
    setTimeout(() => {
        hideLoading();
        showToast(`Successfully deleted ${ids.length} items`, 'success');
        
        // Refresh the page or update table
        location.reload();
    }, 1000);
}

/**
 * Export selected items
 * @param {Array} ids - Array of IDs to export
 */
function exportSelected(ids) {
    showLoading('Preparing export...');
    
    // Simulate export process
    setTimeout(() => {
        hideLoading();
        showToast(`Export completed for ${ids.length} items`, 'success');
        
        // Trigger download
        triggerFileDownload('export.csv');
    }, 1500);
}

/**
 * Update status of selected items
 * @param {Array} ids - Array of IDs
 * @param {string} status - New status
 */
function updateStatus(ids, status) {
    showLoading(`Updating ${ids.length} items...`);
    
    // Simulate API call
    setTimeout(() => {
        hideLoading();
        showToast(`Updated ${ids.length} items to ${status}`, 'success');
        
        // Refresh the page or update UI
        location.reload();
    }, 1000);
}

/**
 * Handle print functionality
 * @param {Event} event - Click event
 */
function handlePrint(event) {
    event.preventDefault();
    
    // Store original display values
    const elementsToHide = document.querySelectorAll('.no-print');
    const originalDisplay = [];
    
    elementsToHide.forEach(el => {
        originalDisplay.push(el.style.display);
        el.style.display = 'none';
    });
    
    // Print
    window.print();
    
    // Restore original display values
    elementsToHide.forEach((el, index) => {
        el.style.display = originalDisplay[index];
    });
}

/**
 * Handle export functionality
 * @param {Event} event - Click event
 */
function handleExport(event) {
    event.preventDefault();
    const format = event.target.dataset.format || 'csv';
    const type = event.target.dataset.exportType || 'current';
    
    showLoading(`Exporting as ${format.toUpperCase()}...`);
    
    // Simulate export
    setTimeout(() => {
        hideLoading();
        showToast(`Export completed successfully`, 'success');
        
        // Trigger download
        const filename = `export-${type}-${new Date().toISOString().split('T')[0]}.${format}`;
        triggerFileDownload(filename);
    }, 2000);
}

/**
 * Trigger file download
 * @param {string} filename - Filename for download
 */
function triggerFileDownload(filename) {
    const link = document.createElement('a');
    link.href = '#';
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Handle modal form submission
 * @param {Event} event - Submit event
 */
function handleModalSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const modalId = form.closest('.modal').id;
    
    // Validate form
    if (!validateForm(form)) {
        return;
    }
    
    showLoading('Saving...');
    
    // Simulate form submission
    setTimeout(() => {
        hideLoading();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
        if (modal) {
            modal.hide();
        }
        
        // Show success message
        showToast('Saved successfully', 'success');
        
        // Reset form
        form.reset();
        
        // Refresh or update page content
        if (form.dataset.refreshOnSubmit === 'true') {
            location.reload();
        }
    }, 1500);
}

/**
 * Preview uploaded file
 * @param {Event} event - Change event
 */
function previewUploadedFile(event) {
    const input = event.target;
    const previewContainer = document.querySelector('.upload-preview');
    
    if (!previewContainer) return;
    
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            if (file.type.startsWith('image/')) {
                previewContainer.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" alt="Preview">`;
            } else {
                previewContainer.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-file me-2"></i>
                        ${file.name} (${formatFileSize(file.size)})
                    </div>
                `;
            }
            previewContainer.classList.remove('d-none');
        };
        
        reader.readAsDataURL(file);
    } else {
        previewContainer.innerHTML = '';
        previewContainer.classList.add('d-none');
    }
}

/**
 * Format file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Set up dashboard auto-refresh
 */
function setupDashboardAutoRefresh() {
    const refreshInterval = parseInt(localStorage.getItem('dashboardRefreshInterval') || '300000'); // 5 minutes default
    
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshDashboard();
        }
    }, refreshInterval);
}

/**
 * Refresh dashboard data
 */
function refreshDashboard() {
    if (!document.querySelector('.dashboard-container')) return;
    
    // Show refreshing indicator
    const refreshBtn = document.querySelector('.btn-refresh');
    if (refreshBtn) {
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i>';
        refreshBtn.disabled = true;
    }
    
    // Simulate data refresh
    setTimeout(() => {
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
            refreshBtn.disabled = false;
        }
        
        // Update last refreshed time
        const lastRefreshed = document.querySelector('.last-refreshed');
        if (lastRefreshed) {
            lastRefreshed.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
        
        // Show notification
        showToast('Dashboard data refreshed', 'info');
    }, 1000);
}

/**
 * Check for notifications
 */
function checkNotifications() {
    // Simulate checking for notifications
    setTimeout(() => {
        const unreadCount = Math.floor(Math.random() * 5); // Random count for demo
        updateNotificationBadge(unreadCount);
    }, 1000);
}

/**
 * Update notification badge
 * @param {number} count - Number of unread notifications
 */
function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 9 ? '9+' : count;
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    }
}

/**
 * Set up auto-save for forms
 */
function setupAutoSave() {
    document.querySelectorAll('.autosave-form').forEach(form => {
        let saveTimeout;
        
        form.addEventListener('input', debounce(() => {
            if (validateForm(form)) {
                saveFormData(form);
            }
        }, 1000));
    });
}

/**
 * Save form data
 * @param {HTMLFormElement} form - Form element
 */
function saveFormData(form) {
    const formData = new FormData(form);
    const formId = form.id || 'unsaved-form';
    
    // Store in localStorage
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    
    localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    
    // Show auto-save indicator
    showAutoSaveIndicator();
}

/**
 * Show auto-save indicator
 */
function showAutoSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'autosave-indicator alert alert-success alert-dismissible fade show position-fixed';
    indicator.style.cssText = 'bottom: 20px; right: 20px; z-index: 1050;';
    indicator.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        Changes saved automatically
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(indicator);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        if (indicator.parentNode) {
            indicator.remove();
        }
    }, 3000);
}

/**
 * Load user preferences
 */
function loadUserPreferences() {
    // Load theme preference
    const theme = localStorage.getItem('theme') || 'light';
    setTheme(theme);
    
    // Load sidebar state
    const sidebarOpen = localStorage.getItem('sidebarOpen') === 'true';
    if (sidebarOpen && window.innerWidth < 768) {
        toggleSidebar();
    }
    
    // Load table preferences
    loadTablePreferences();
}

/**
 * Initialize theme
 */
function initializeTheme() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        
        // Set initial icon
        const currentTheme = localStorage.getItem('theme') || 'light';
        updateThemeIcon(currentTheme);
    }
}

/**
 * Toggle theme between light and dark
 */
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

/**
 * Set theme
 * @param {string} theme - Theme name ('light' or 'dark')
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
}

/**
 * Update theme icon
 * @param {string} theme - Current theme
 */
function updateThemeIcon(theme) {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
        themeToggle.title = `Switch to ${theme === 'light' ? 'dark' : 'light'} theme`;
    }
}

/**
 * Load table preferences
 */
function loadTablePreferences() {
    const tables = document.querySelectorAll('table[data-table-id]');
    tables.forEach(table => {
        const tableId = table.dataset.tableId;
        const prefs = JSON.parse(localStorage.getItem(`table_prefs_${tableId}`) || '{}');
        
        // Apply column visibility
        if (prefs.visibleColumns) {
            applyColumnVisibility(table, prefs.visibleColumns);
        }
        
        // Apply sort order
        if (prefs.sortColumn && prefs.sortDirection) {
            applySortOrder(table, prefs.sortColumn, prefs.sortDirection);
        }
    });
}

/**
 * Apply column visibility
 * @param {HTMLTableElement} table - Table element
 * @param {Array} visibleColumns - Array of column indices to show
 */
function applyColumnVisibility(table, visibleColumns) {
    const headers = table.querySelectorAll('th');
    const rows = table.querySelectorAll('tbody tr');
    
    headers.forEach((header, index) => {
        if (!visibleColumns.includes(index)) {
            header.style.display = 'none';
            rows.forEach(row => {
                const cell = row.cells[index];
                if (cell) cell.style.display = 'none';
            });
        }
    });
}

/**
 * Apply sort order
 * @param {HTMLTableElement} table - Table element
 * @param {number} columnIndex - Column index to sort by
 * @param {string} direction - Sort direction ('asc' or 'desc')
 */
function applySortOrder(table, columnIndex, direction) {
    // Implement table sorting logic
    console.log(`Sorting table by column ${columnIndex} in ${direction} order`);
}

/**
 * Show loading overlay
 * @param {string} message - Loading message
 */
function showLoading(message = 'Loading...') {
    let overlay = document.querySelector('.loading-overlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        overlay.style.cssText = 'background: rgba(255, 255, 255, 0.8); z-index: 9999;';
        overlay.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary-green" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        const messageEl = overlay.querySelector('p');
        if (messageEl) {
            messageEl.textContent = message;
        }
        overlay.classList.remove('d-none');
    }
    
    document.body.style.overflow = 'hidden';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.classList.add('d-none');
        setTimeout(() => {
            if (overlay.parentNode) {
                overlay.remove();
            }
        }, 300);
    }
    
    document.body.style.overflow = '';
}

/**
 * Show toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    let container;
    
    if (!toastContainer) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.cssText = 'z-index: 1055;';
        document.body.appendChild(container);
    } else {
        container = toastContainer;
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">
                    <i class="fas fa-${getToastIcon(type)} me-2"></i>
                    ${type.charAt(0).toUpperCase() + type.slice(1)}
                </strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastEl = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 5000
    });
    
    toast.show();
    
    // Remove toast from DOM after hiding
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

/**
 * Get toast icon based on type
 * @param {string} type - Toast type
 * @returns {string} Icon class suffix
 */
function getToastIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        case 'info': return 'info-circle';
        default: return 'info-circle';
    }
}

/**
 * Validate form
 * @param {HTMLFormElement} form - Form element
 * @returns {boolean} True if form is valid
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    // Clear previous errors
    form.querySelectorAll('.is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });
    
    form.querySelectorAll('.invalid-feedback').forEach(el => {
        el.remove();
    });
    
    // Validate required fields
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            markFieldInvalid(field, 'This field is required');
            isValid = false;
        } else if (field.type === 'email' && !isValidEmail(field.value)) {
            markFieldInvalid(field, 'Please enter a valid email address');
            isValid = false;
        } else if (field.type === 'tel' && !isValidPhone(field.value)) {
            markFieldInvalid(field, 'Please enter a valid phone number');
            isValid = false;
        } else if (field.type === 'number' && field.min && parseFloat(field.value) < parseFloat(field.min)) {
            markFieldInvalid(field, `Value must be at least ${field.min}`);
            isValid = false;
        } else if (field.type === 'number' && field.max && parseFloat(field.value) > parseFloat(field.max)) {
            markFieldInvalid(field, `Value must be at most ${field.max}`);
            isValid = false;
        }
    });
    
    // Validate passwords match
    const password = form.querySelector('input[type="password"]');
    const confirmPassword = form.querySelector('input[name="confirm_password"]');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
        markFieldInvalid(confirmPassword, 'Passwords do not match');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Mark field as invalid
 * @param {HTMLElement} field - Input field
 * @param {string} message - Error message
 */
function markFieldInvalid(field, message) {
    field.classList.add('is-invalid');
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    
    field.parentNode.appendChild(feedback);
}

/**
 * Check if email is valid
 * @param {string} email - Email address
 * @returns {boolean} True if email is valid
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Check if phone number is valid
 * @param {string} phone - Phone number
 * @returns {boolean} True if phone is valid
 */
function isValidPhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone.replace(/[\s\-\(\)\.]/g, ''));
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Make utility functions available globally
window.XpertFarmerIMS = {
    showToast,
    showLoading,
    hideLoading,
    validateForm,
    debounce
};