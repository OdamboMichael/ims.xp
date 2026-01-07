/**
 * Xpert Farmer IMS - Forms JavaScript
 * Handles form validation, submission, and interactions
 */

// Form state management
const formStates = new Map();

/**
 * Initialize all forms on the page
 */
function initializeForms() {
    // Setup form validation
    setupFormValidation();
    
    // Setup auto-save
    setupAutoSave();
    
    // Setup form enhancements
    setupFormEnhancements();
    
    // Load saved form states
    loadFormStates();
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    // Add validation to all forms with data-validate attribute
    document.querySelectorAll('form[data-validate]').forEach(form => {
        setupFormValidationFor(form);
    });
    
    // Real-time validation for inputs
    document.querySelectorAll('.validate-on-input').forEach(input => {
        input.addEventListener('input', debounce(validateInput, 500));
    });
    
    // Validate on blur
    document.querySelectorAll('.validate-on-blur').forEach(input => {
        input.addEventListener('blur', validateInput);
    });
}

/**
 * Setup form validation for specific form
 * @param {HTMLFormElement} form - Form element
 */
function setupFormValidationFor(form) {
    // Clear previous validation
    clearFormValidation(form);
    
    // Add submit handler
    form.addEventListener('submit', function(event) {
        if (!validateForm(form)) {
            event.preventDefault();
            showFormErrors(form);
        }
    });
    
    // Add input handlers for real-time validation
    form.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('input', function() {
            validateField(this);
        });
        
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

/**
 * Validate entire form
 * @param {HTMLFormElement} form - Form element
 * @returns {boolean} True if form is valid
 */
function validateForm(form) {
    let isValid = true;
    
    // Clear previous errors
    clearFormValidation(form);
    
    // Validate all fields
    const fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Validate custom rules
    const customRules = form.querySelectorAll('[data-custom-validation]');
    customRules.forEach(element => {
        if (!validateCustomRule(element)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Validate single field
 * @param {HTMLElement} field - Form field
 * @returns {boolean} True if field is valid
 */
function validateField(field) {
    // Skip disabled and hidden fields
    if (field.disabled || field.type === 'hidden') {
        return true;
    }
    
    const value = field.value.trim();
    const fieldName = field.name || field.id;
    let isValid = true;
    let errorMessage = '';
    
    // Check required fields
    if (field.required && !value) {
        isValid = false;
        errorMessage = field.dataset.requiredMessage || 'This field is required';
    }
    
    // Check min length
    if (isValid && field.minLength && value.length < field.minLength) {
        isValid = false;
        errorMessage = field.dataset.minLengthMessage || 
            `Minimum length is ${field.minLength} characters`;
    }
    
    // Check max length
    if (isValid && field.maxLength && value.length > field.maxLength) {
        isValid = false;
        errorMessage = field.dataset.maxLengthMessage || 
            `Maximum length is ${field.maxLength} characters`;
    }
    
    // Check pattern
    if (isValid && field.pattern) {
        const pattern = new RegExp(field.pattern);
        if (!pattern.test(value)) {
            isValid = false;
            errorMessage = field.dataset.patternMessage || 
                'Please enter a valid value';
        }
    }
    
    // Type-specific validation
    if (isValid) {
        switch(field.type) {
            case 'email':
                if (!isValidEmail(value)) {
                    isValid = false;
                    errorMessage = field.dataset.emailMessage || 
                        'Please enter a valid email address';
                }
                break;
                
            case 'tel':
                if (!isValidPhone(value)) {
                    isValid = false;
                    errorMessage = field.dataset.phoneMessage || 
                        'Please enter a valid phone number';
                }
                break;
                
            case 'url':
                if (!isValidUrl(value)) {
                    isValid = false;
                    errorMessage = field.dataset.urlMessage || 
                        'Please enter a valid URL';
                }
                break;
                
            case 'number':
                if (field.min && parseFloat(value) < parseFloat(field.min)) {
                    isValid = false;
                    errorMessage = field.dataset.minMessage || 
                        `Minimum value is ${field.min}`;
                }
                if (field.max && parseFloat(value) > parseFloat(field.max)) {
                    isValid = false;
                    errorMessage = field.dataset.maxMessage || 
                        `Maximum value is ${field.max}`;
                }
                break;
                
            case 'date':
                if (!isValidDate(value)) {
                    isValid = false;
                    errorMessage = field.dataset.dateMessage || 
                        'Please enter a valid date';
                }
                break;
        }
    }
    
    // Update field state
    updateFieldState(field, isValid, errorMessage);
    
    // Store validation state
    formStates.set(fieldName, { isValid, errorMessage });
    
    return isValid;
}

/**
 * Validate input in real-time
 * @param {Event} event - Input event
 */
function validateInput(event) {
    const field = event.target;
    validateField(field);
}

/**
 * Validate custom rule
 * @param {HTMLElement} element - Element with custom validation
 * @returns {boolean} True if rule passes
 */
function validateCustomRule(element) {
    const rule = element.dataset.customValidation;
    let isValid = true;
    let errorMessage = '';
    
    switch(rule) {
        case 'password-match':
            const password = document.querySelector(element.dataset.matchField);
            const confirmPassword = element;
            
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                isValid = false;
                errorMessage = 'Passwords do not match';
            }
            break;
            
        case 'date-range':
            const startDate = document.querySelector(element.dataset.startDate);
            const endDate = document.querySelector(element.dataset.endDate);
            
            if (startDate && endDate && new Date(startDate.value) > new Date(endDate.value)) {
                isValid = false;
                errorMessage = 'End date must be after start date';
            }
            break;
            
        case 'min-selection':
            const checkboxes = document.querySelectorAll(element.dataset.selectionGroup);
            const selected = Array.from(checkboxes).filter(cb => cb.checked).length;
            const min = parseInt(element.dataset.minSelection) || 1;
            
            if (selected < min) {
                isValid = false;
                errorMessage = `Please select at least ${min} option${min > 1 ? 's' : ''}`;
            }
            break;
            
        case 'unique':
            // Check if value is unique (would require API call)
            isValid = true; // Implement uniqueness check
            break;
    }
    
    // Update element state
    if (!isValid) {
        markElementInvalid(element, errorMessage);
    } else {
        markElementValid(element);
    }
    
    return isValid;
}

/**
 * Update field validation state
 * @param {HTMLElement} field - Form field
 * @param {boolean} isValid - Validation result
 * @param {string} errorMessage - Error message if invalid
 */
function updateFieldState(field, isValid, errorMessage = '') {
    // Remove previous validation classes and messages
    field.classList.remove('is-valid', 'is-invalid');
    
    const feedback = field.nextElementSibling;
    if (feedback && feedback.classList.contains('valid-feedback')) {
        feedback.remove();
    }
    
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.remove();
    }
    
    // Add appropriate classes and messages
    if (isValid) {
        field.classList.add('is-valid');
        
        // Add success message if specified
        const successMessage = field.dataset.successMessage;
        if (successMessage) {
            const successFeedback = document.createElement('div');
            successFeedback.className = 'valid-feedback';
            successFeedback.textContent = successMessage;
            field.parentNode.appendChild(successFeedback);
        }
    } else {
        field.classList.add('is-invalid');
        
        // Add error message
        const errorFeedback = document.createElement('div');
        errorFeedback.className = 'invalid-feedback';
        errorFeedback.textContent = errorMessage;
        field.parentNode.appendChild(errorFeedback);
    }
    
    // Update form group state
    const formGroup = field.closest('.form-group, .mb-3');
    if (formGroup) {
        formGroup.classList.remove('has-error', 'has-success');
        
        if (isValid) {
            formGroup.classList.add('has-success');
        } else {
            formGroup.classList.add('has-error');
        }
    }
}

/**
 * Mark element as invalid
 * @param {HTMLElement} element - Element to mark
 * @param {string} message - Error message
 */
function markElementInvalid(element, message) {
    element.classList.add('is-invalid');
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    element.parentNode.appendChild(feedback);
}

/**
 * Mark element as valid
 * @param {HTMLElement} element - Element to mark
 */
function markElementValid(element) {
    element.classList.remove('is-invalid');
    element.classList.add('is-valid');
    
    const feedback = element.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.remove();
    }
}

/**
 * Clear form validation
 * @param {HTMLFormElement} form - Form element
 */
function clearFormValidation(form) {
    // Clear field states
    form.querySelectorAll('.is-valid, .is-invalid').forEach(field => {
        field.classList.remove('is-valid', 'is-invalid');
    });
    
    // Clear feedback messages
    form.querySelectorAll('.valid-feedback, .invalid-feedback').forEach(feedback => {
        feedback.remove();
    });
    
    // Clear form group states
    form.querySelectorAll('.has-success, .has-error').forEach(group => {
        group.classList.remove('has-success', 'has-error');
    });
    
    // Clear form states storage
    formStates.clear();
}

/**
 * Show form errors
 * @param {HTMLFormElement} form - Form element
 */
function showFormErrors(form) {
    // Find first invalid field
    const firstInvalid = form.querySelector('.is-invalid');
    if (firstInvalid) {
        firstInvalid.focus();
        
        // Scroll to error
        firstInvalid.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
    
    // Show error summary
    showErrorSummary(form);
}

/**
 * Show error summary
 * @param {HTMLFormElement} form - Form element
 */
function showErrorSummary(form) {
    // Remove existing summary
    const existingSummary = form.querySelector('.error-summary');
    if (existingSummary) {
        existingSummary.remove();
    }
    
    // Get all errors
    const errors = [];
    form.querySelectorAll('.is-invalid').forEach(field => {
        const fieldName = field.name || field.id;
        const errorMessage = field.nextElementSibling?.textContent || 'Invalid value';
        const label = form.querySelector(`label[for="${field.id}"]`)?.textContent || fieldName;
        
        errors.push({
            field: field,
            label: label,
            message: errorMessage
        });
    });
    
    if (errors.length > 0) {
        // Create error summary
        const summary = document.createElement('div');
        summary.className = 'error-summary alert alert-danger';
        summary.setAttribute('role', 'alert');
        
        let html = `
            <div class="d-flex align-items-center mb-2">
                <i class="fas fa-exclamation-circle me-2"></i>
                <strong>Please correct the following errors:</strong>
            </div>
            <ul class="mb-0">
        `;
        
        errors.forEach(error => {
            html += `
                <li>
                    <a href="#${error.field.id}" class="text-danger" onclick="document.getElementById('${error.field.id}').focus(); return false;">
                        ${error.label}: ${error.message}
                    </a>
                </li>
            `;
        });
        
        html += '</ul>';
        summary.innerHTML = html;
        
        // Insert at top of form
        form.insertBefore(summary, form.firstChild);
        
        // Scroll to summary
        summary.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Setup auto-save for forms
 */
function setupAutoSave() {
    document.querySelectorAll('.autosave-form').forEach(form => {
        setupAutoSaveFor(form);
    });
}

/**
 * Setup auto-save for specific form
 * @param {HTMLFormElement} form - Form element
 */
function setupAutoSaveFor(form) {
    const formId = form.id || 'form-' + Math.random().toString(36).substr(2, 9);
    let saveTimeout;
    
    // Load saved data
    loadSavedFormData(form, formId);
    
    // Auto-save on input
    form.addEventListener('input', debounce(() => {
        saveFormData(form, formId);
    }, 1000));
    
    // Save on blur
    form.addEventListener('blur', (event) => {
        if (event.target.matches('input, select, textarea')) {
            saveFormData(form, formId);
        }
    }, true);
    
    // Clear saved data on successful submit
    form.addEventListener('submit', () => {
        clearSavedFormData(formId);
    });
}

/**
 * Save form data
 * @param {HTMLFormElement} form - Form element
 * @param {string} formId - Form identifier
 */
function saveFormData(form, formId) {
    const formData = new FormData(form);
    const data = {};
    
    formData.forEach((value, key) => {
        data[key] = value;
    });
    
    localStorage.setItem(`form_${formId}`, JSON.stringify(data));
    localStorage.setItem(`form_${formId}_timestamp`, Date.now());
    
    showAutoSaveIndicator();
}

/**
 * Load saved form data
 * @param {HTMLFormElement} form - Form element
 * @param {string} formId - Form identifier
 */
function loadSavedFormData(form, formId) {
    const savedData = localStorage.getItem(`form_${formId}`);
    const timestamp = localStorage.getItem(`form_${formId}_timestamp`);
    
    if (savedData && timestamp) {
        const data = JSON.parse(savedData);
        const age = Date.now() - parseInt(timestamp);
        
        // Only load if less than 24 hours old
        if (age < 24 * 60 * 60 * 1000) {
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field && !field.disabled) {
                    field.value = data[key];
                    
                    // Trigger change event
                    field.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
            
            // Show restore notification
            showRestoreNotification(form);
        }
    }
}

/**
 * Clear saved form data
 * @param {string} formId - Form identifier
 */
function clearSavedFormData(formId) {
    localStorage.removeItem(`form_${formId}`);
    localStorage.removeItem(`form_${formId}_timestamp`);
}

/**
 * Show auto-save indicator
 */
function showAutoSaveIndicator() {
    let indicator = document.querySelector('.autosave-indicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'autosave-indicator alert alert-success alert-dismissible fade show position-fixed';
        indicator.style.cssText = 'bottom: 20px; right: 20px; z-index: 1050; max-width: 300px;';
        indicator.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <span class="autosave-text">Changes saved</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(indicator);
    } else {
        const text = indicator.querySelector('.autosave-text');
        if (text) {
            text.textContent = 'Changes saved';
        }
        indicator.classList.remove('d-none');
    }
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (indicator.parentNode) {
            indicator.classList.add('d-none');
        }
    }, 3000);
}

/**
 * Show restore notification
 * @param {HTMLFormElement} form - Form element
 */
function showRestoreNotification(form) {
    const notification = document.createElement('div');
    notification.className = 'restore-notification alert alert-info alert-dismissible fade show';
    notification.innerHTML = `
        <i class="fas fa-history me-2"></i>
        <strong>Restored unsaved changes</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <div class="mt-2">
            <button type="button" class="btn btn-sm btn-outline-primary me-2" onclick="clearForm('${form.id}')">
                Clear restored data
            </button>
            <button type="button" class="btn btn-sm btn-primary" onclick="saveForm('${form.id}')">
                Keep changes
            </button>
        </div>
    `;
    
    form.parentNode.insertBefore(notification, form);
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 10000);
}

/**
 * Setup form enhancements
 */
function setupFormEnhancements() {
    // Character counters
    setupCharacterCounters();
    
    // Password strength indicators
    setupPasswordStrength();
    
    // Date pickers
    setupDatePickers();
    
    // File upload enhancements
    setupFileUploads();
    
    // Select2-like enhancements
    setupSelectEnhancements();
    
    // Dynamic form fields
    setupDynamicFields();
}

/**
 * Setup character counters
 */
function setupCharacterCounters() {
    document.querySelectorAll('[data-max-length]').forEach(field => {
        const maxLength = parseInt(field.dataset.maxLength);
        const counterId = field.id + '-counter';
        
        // Create counter element
        let counter = document.getElementById(counterId);
        if (!counter) {
            counter = document.createElement('small');
            counter.id = counterId;
            counter.className = 'form-text text-muted character-counter';
            field.parentNode.appendChild(counter);
        }
        
        // Update counter on input
        const updateCounter = () => {
            const length = field.value.length;
            const remaining = maxLength - length;
            
            counter.textContent = `${length} / ${maxLength} characters`;
            counter.className = `form-text character-counter ${remaining < 0 ? 'text-danger' : 'text-muted'}`;
            
            if (remaining < 0) {
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        };
        
        field.addEventListener('input', updateCounter);
        updateCounter(); // Initial update
    });
}

/**
 * Setup password strength indicator
 */
function setupPasswordStrength() {
    document.querySelectorAll('input[type="password"]').forEach(passwordField => {
        const strengthId = passwordField.id + '-strength';
        const strengthContainer = document.getElementById(strengthId);
        
        if (!strengthContainer) {
            const container = document.createElement('div');
            container.id = strengthId;
            container.className = 'password-strength mt-2';
            passwordField.parentNode.appendChild(container);
        }
        
        passwordField.addEventListener('input', debounce(() => {
            updatePasswordStrength(passwordField);
        }, 300));
    });
}

/**
 * Update password strength indicator
 * @param {HTMLInputElement} passwordField - Password input field
 */
function updatePasswordStrength(passwordField) {
    const password = passwordField.value;
    const strengthId = passwordField.id + '-strength';
    const strengthContainer = document.getElementById(strengthId);
    
    if (!strengthContainer) return;
    
    // Calculate strength
    let score = 0;
    let feedback = '';
    
    // Length check
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    
    // Complexity checks
    if (/[a-z]/.test(password)) score += 1; // Lowercase
    if (/[A-Z]/.test(password)) score += 1; // Uppercase
    if (/[0-9]/.test(password)) score += 1; // Numbers
    if (/[^A-Za-z0-9]/.test(password)) score += 1; // Special characters
    
    // Determine strength level
    let strength, color, width;
    
    if (password.length === 0) {
        strength = 'No password';
        color = '#6c757d';
        width = '0%';
        feedback = '';
    } else if (score <= 2) {
        strength = 'Weak';
        color = '#dc3545';
        width = '25%';
        feedback = 'Add more characters, mix case, numbers, and symbols';
    } else if (score <= 4) {
        strength = 'Fair';
        color = '#ffc107';
        width = '50%';
        feedback = 'Good start, but could be stronger';
    } else if (score <= 5) {
        strength = 'Good';
        color = '#28a745';
        width = '75%';
        feedback = 'Strong password';
    } else {
        strength = 'Excellent';
        color = '#22C55E';
        width = '100%';
        feedback = 'Very strong password';
    }
    
    // Update display
    strengthContainer.innerHTML = `
        <div class="d-flex justify-content-between mb-1">
            <small class="text-muted">Password strength:</small>
            <small class="text-${score <= 2 ? 'danger' : score <= 4 ? 'warning' : 'success'}">${strength}</small>
        </div>
        <div class="progress" style="height: 4px;">
            <div class="progress-bar" role="progressbar" style="width: ${width}; background-color: ${color};"></div>
        </div>
        ${feedback ? `<small class="form-text text-muted mt-1">${feedback}</small>` : ''}
    `;
}

/**
 * Setup date pickers
 */
function setupDatePickers() {
    document.querySelectorAll('input[type="date"]').forEach(dateInput => {
        // Add date picker enhancement if needed
        if (!dateInput.type) {
            dateInput.type = 'date';
        }
        
        // Set min/max dates if specified
        if (dateInput.dataset.minDate) {
            dateInput.min = dateInput.dataset.minDate;
        }
        
        if (dateInput.dataset.maxDate) {
            dateInput.max = dateInput.dataset.maxDate;
        }
        
        // Set default to today if specified
        if (dateInput.dataset.defaultToday === 'true') {
            dateInput.valueAsDate = new Date();
        }
    });
}

/**
 * Setup file upload enhancements
 */
function setupFileUploads() {
    document.querySelectorAll('input[type="file"]').forEach(fileInput => {
        const wrapper = fileInput.closest('.file-upload-wrapper');
        
        if (!wrapper) {
            // Create wrapper
            const newWrapper = document.createElement('div');
            newWrapper.className = 'file-upload-wrapper';
            
            // Wrap input
            fileInput.parentNode.insertBefore(newWrapper, fileInput);
            newWrapper.appendChild(fileInput);
            
            // Add custom button
            const customButton = document.createElement('button');
            customButton.type = 'button';
            customButton.className = 'btn btn-outline-primary btn-sm';
            customButton.innerHTML = '<i class="fas fa-upload me-1"></i> Choose File';
            newWrapper.appendChild(customButton);
            
            // Add file name display
            const fileNameDisplay = document.createElement('span');
            fileNameDisplay.className = 'file-name ms-2 text-muted';
            newWrapper.appendChild(fileNameDisplay);
            
            // Update display on file selection
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    const names = Array.from(this.files).map(f => f.name);
                    fileNameDisplay.textContent = names.join(', ');
                    customButton.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Change';
                } else {
                    fileNameDisplay.textContent = 'No file chosen';
                    customButton.innerHTML = '<i class="fas fa-upload me-1"></i> Choose File';
                }
            });
            
            // Trigger file dialog on button click
            customButton.addEventListener('click', () => {
                fileInput.click();
            });
        }
        
        // Add file type validation
        if (fileInput.accept) {
            fileInput.addEventListener('change', function() {
                const allowedTypes = this.accept.split(',').map(t => t.trim());
                const files = Array.from(this.files);
                
                const invalidFiles = files.filter(file => {
                    return !allowedTypes.some(type => {
                        if (type.startsWith('.')) {
                            return file.name.toLowerCase().endsWith(type.toLowerCase());
                        }
                        return file.type.match(type.replace('*', '.*'));
                    });
                });
                
                if (invalidFiles.length > 0) {
                    alert(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`);
                    this.value = '';
                }
            });
        }
        
        // Add file size validation
        if (fileInput.dataset.maxSize) {
            const maxSize = parseFileSize(fileInput.dataset.maxSize);
            
            fileInput.addEventListener('change', function() {
                const files = Array.from(this.files);
                const oversizedFiles = files.filter(file => file.size > maxSize);
                
                if (oversizedFiles.length > 0) {
                    alert(`File size exceeds limit. Maximum size: ${formatFileSize(maxSize)}`);
                    this.value = '';
                }
            });
        }
    });
}

/**
 * Setup select enhancements
 */
function setupSelectEnhancements() {
    document.querySelectorAll('select[multiple]').forEach(select => {
        // Add search functionality for large select boxes
        if (select.options.length > 10) {
            addSelectSearch(select);
        }
        
        // Add select all/none buttons
        if (select.dataset.enhanced === 'true') {
            addSelectControls(select);
        }
    });
}

/**
 * Add search to select box
 * @param {HTMLSelectElement} select - Select element
 */
function addSelectSearch(select) {
    const wrapper = document.createElement('div');
    wrapper.className = 'select-search-wrapper';
    
    // Create search input
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control form-control-sm mb-2';
    searchInput.placeholder = 'Search options...';
    
    // Wrap select
    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
    wrapper.insertBefore(searchInput, select);
    
    // Filter options on search
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        Array.from(select.options).forEach(option => {
            if (option.text.toLowerCase().includes(searchTerm)) {
                option.style.display = '';
            } else {
                option.style.display = 'none';
            }
        });
    });
}

/**
 * Add controls to select box
 * @param {HTMLSelectElement} select - Select element
 */
function addSelectControls(select) {
    const controlDiv = document.createElement('div');
    controlDiv.className = 'select-controls mb-2';
    
    const selectAllBtn = document.createElement('button');
    selectAllBtn.type = 'button';
    selectAllBtn.className = 'btn btn-sm btn-outline-primary me-2';
    selectAllBtn.textContent = 'Select All';
    
    const selectNoneBtn = document.createElement('button');
    selectNoneBtn.type = 'button';
    selectNoneBtn.className = 'btn btn-sm btn-outline-secondary';
    selectNoneBtn.textContent = 'Select None';
    
    controlDiv.appendChild(selectAllBtn);
    controlDiv.appendChild(selectNoneBtn);
    
    select.parentNode.insertBefore(controlDiv, select);
    
    // Add event listeners
    selectAllBtn.addEventListener('click', () => {
        Array.from(select.options).forEach(option => {
            option.selected = true;
        });
        select.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    selectNoneBtn.addEventListener('click', () => {
        Array.from(select.options).forEach(option => {
            option.selected = false;
        });
        select.dispatchEvent(new Event('change', { bubbles: true }));
    });
}

/**
 * Setup dynamic form fields
 */
function setupDynamicFields() {
    // Add more button for repeating fields
    document.querySelectorAll('.btn-add-field').forEach(button => {
        button.addEventListener('click', function() {
            const templateId = this.dataset.template;
            const containerId = this.dataset.container;
            
            addDynamicField(templateId, containerId);
        });
    });
    
    // Remove field buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('btn-remove-field')) {
            event.preventDefault();
            removeDynamicField(event.target);
        }
    });
}

/**
 * Add dynamic field
 * @param {string} templateId - Template element ID
 * @param {string} containerId - Container element ID
 */
function addDynamicField(templateId, containerId) {
    const template = document.getElementById(templateId);
    const container = document.getElementById(containerId);
    
    if (!template || !container) return;
    
    const clone = template.content.cloneNode(true);
    const newField = clone.querySelector('.dynamic-field');
    
    if (newField) {
        // Update field names with unique index
        const index = container.children.length;
        newField.querySelectorAll('[name]').forEach(field => {
            const name = field.getAttribute('name');
            field.setAttribute('name', name.replace('__index__', index));
            field.setAttribute('id', field.id ? field.id.replace('__index__', index) : '');
        });
        
        // Update labels
        newField.querySelectorAll('label[for]').forEach(label => {
            const forAttr = label.getAttribute('for');
            label.setAttribute('for', forAttr.replace('__index__', index));
        });
        
        container.appendChild(newField);
        
        // Initialize any nested forms
        initializeFormsInElement(newField);
    }
}

/**
 * Remove dynamic field
 * @param {HTMLElement} button - Remove button
 */
function removeDynamicField(button) {
    const field = button.closest('.dynamic-field');
    if (field && !field.hasAttribute('data-required')) {
        field.remove();
    }
}

/**
 * Initialize forms in specific element
 * @param {HTMLElement} element - Element containing forms
 */
function initializeFormsInElement(element) {
    // Re-initialize form validation
    element.querySelectorAll('form[data-validate]').forEach(form => {
        setupFormValidationFor(form);
    });
    
    // Re-initialize character counters
    element.querySelectorAll('[data-max-length]').forEach(field => {
        // This would need to call setupCharacterCounters for the specific field
    });
}

/**
 * Load saved form states
 */
function loadFormStates() {
    // Load from localStorage
    const savedStates = localStorage.getItem('formStates');
    if (savedStates) {
        const states = JSON.parse(savedStates);
        Object.keys(states).forEach(formId => {
            // Apply saved states to forms
            console.log(`Loaded state for form: ${formId}`);
        });
    }
}

/**
 * Parse file size string
 * @param {string} sizeString - Size string (e.g., "10MB", "1GB")
 * @returns {number} Size in bytes
 */
function parseFileSize(sizeString) {
    const units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024,
        'TB': 1024 * 1024 * 1024 * 1024
    };
    
    const match = sizeString.match(/^(\d+(?:\.\d+)?)\s*([KMGT]?B)$/i);
    if (match) {
        const value = parseFloat(match[1]);
        const unit = match[2].toUpperCase();
        return value * (units[unit] || 1);
    }
    
    return parseInt(sizeString) || 0;
}

/**
 * Format file size
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size string
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Check if email is valid
 * @param {string} email - Email address
 * @returns {boolean} True if valid
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Check if phone number is valid
 * @param {string} phone - Phone number
 * @returns {boolean} True if valid
 */
function isValidPhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone.replace(/[\s\-\(\)\.]/g, ''));
}

/**
 * Check if URL is valid
 * @param {string} url - URL
 * @returns {boolean} True if valid
 */
function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

/**
 * Check if date is valid
 * @param {string} dateString - Date string
 * @returns {boolean} True if valid
 */
function isValidDate(dateString) {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
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

// Initialize forms when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeForms);

// Make form functions available globally
window.XpertFarmerForms = {
    validateForm,
    clearFormValidation,
    showFormErrors,
    saveFormData,
    loadSavedFormData,
    clearSavedFormData
};