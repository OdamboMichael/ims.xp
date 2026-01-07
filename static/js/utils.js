/**
 * Xpert Farmer IMS - Utilities JavaScript
 * General utility functions for the application
 */

// Utility namespace
const XpertFarmerUtils = {
    // DOM Utilities
    dom: {
        /**
         * Create element with attributes and children
         * @param {string} tag - HTML tag name
         * @param {Object} attributes - Element attributes
         * @param {Array|string} children - Child elements or text
         * @returns {HTMLElement} Created element
         */
        createElement(tag, attributes = {}, children = []) {
            const element = document.createElement(tag);
            
            // Set attributes
            Object.keys(attributes).forEach(key => {
                if (key === 'className') {
                    element.className = attributes[key];
                } else if (key === 'htmlFor') {
                    element.setAttribute('for', attributes[key]);
                } else if (key.startsWith('data-')) {
                    element.setAttribute(key, attributes[key]);
                } else if (key === 'style' && typeof attributes[key] === 'object') {
                    Object.assign(element.style, attributes[key]);
                } else {
                    element.setAttribute(key, attributes[key]);
                }
            });
            
            // Add children
            if (typeof children === 'string') {
                element.textContent = children;
            } else if (Array.isArray(children)) {
                children.forEach(child => {
                    if (typeof child === 'string') {
                        element.appendChild(document.createTextNode(child));
                    } else if (child instanceof Node) {
                        element.appendChild(child);
                    }
                });
            }
            
            return element;
        },
        
        /**
         * Remove all children from element
         * @param {HTMLElement} element - Parent element
         */
        removeAllChildren(element) {
            while (element.firstChild) {
                element.removeChild(element.firstChild);
            }
        },
        
        /**
         * Toggle element visibility
         * @param {HTMLElement} element - Element to toggle
         * @param {boolean} show - Force show/hide (optional)
         */
        toggleVisibility(element, show = null) {
            if (show === null) {
                show = element.style.display === 'none';
            }
            
            element.style.display = show ? '' : 'none';
        },
        
        /**
         * Add or remove CSS class with animation
         * @param {HTMLElement} element - Target element
         * @param {string} className - CSS class name
         * @param {boolean} add - True to add, false to remove
         */
        animateClass(element, className, add = true) {
            if (add) {
                element.classList.add(className);
            } else {
                element.classList.remove(className);
            }
            
            // Force reflow for animation
            void element.offsetWidth;
        },
        
        /**
         * Scroll element into view smoothly
         * @param {HTMLElement} element - Element to scroll to
         * @param {Object} options - Scroll options
         */
        scrollToElement(element, options = {}) {
            const defaultOptions = {
                behavior: 'smooth',
                block: 'start',
                inline: 'nearest'
            };
            
            element.scrollIntoView({ ...defaultOptions, ...options });
        },
        
        /**
         * Check if element is in viewport
         * @param {HTMLElement} element - Element to check
         * @param {number} offset - Viewport offset
         * @returns {boolean} True if element is in viewport
         */
        isInViewport(element, offset = 0) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + offset &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth) + offset
            );
        },
        
        /**
         * Get computed style value
         * @param {HTMLElement} element - Target element
         * @param {string} property - CSS property name
         * @returns {string} Computed style value
         */
        getComputedStyle(element, property) {
            return window.getComputedStyle(element).getPropertyValue(property);
        }
    },
    
    // String Utilities
    string: {
        /**
         * Capitalize first letter of string
         * @param {string} str - Input string
         * @returns {string} Capitalized string
         */
        capitalize(str) {
            return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
        },
        
        /**
         * Convert string to title case
         * @param {string} str - Input string
         * @returns {string} Title cased string
         */
        titleCase(str) {
            return str.replace(/\w\S*/g, function(txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            });
        },
        
        /**
         * Truncate string with ellipsis
         * @param {string} str - Input string
         * @param {number} length - Maximum length
         * @param {string} suffix - Suffix to add (default: '...')
         * @returns {string} Truncated string
         */
        truncate(str, length, suffix = '...') {
            if (str.length <= length) return str;
            return str.substr(0, length - suffix.length) + suffix;
        },
        
        /**
         * Generate random string
         * @param {number} length - Length of string
         * @returns {string} Random string
         */
        random(length = 8) {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            let result = '';
            for (let i = 0; i < length; i++) {
                result += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            return result;
        },
        
        /**
         * Convert string to slug
         * @param {string} str - Input string
         * @returns {string} Slugified string
         */
        slugify(str) {
            return str
                .toLowerCase()
                .trim()
                .replace(/[^\w\s-]/g, '')
                .replace(/[\s_-]+/g, '-')
                .replace(/^-+|-+$/g, '');
        },
        
        /**
         * Strip HTML tags from string
         * @param {string} html - HTML string
         * @returns {string} Plain text
         */
        stripTags(html) {
            const div = document.createElement('div');
            div.innerHTML = html;
            return div.textContent || div.innerText || '';
        },
        
        /**
         * Escape HTML special characters
         * @param {string} str - Input string
         * @returns {string} Escaped string
         */
        escapeHtml(str) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return str.replace(/[&<>"']/g, m => map[m]);
        },
        
        /**
         * Format number with commas
         * @param {number} num - Number to format
         * @returns {string} Formatted number
         */
        formatNumber(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        },
        
        /**
         * Format currency
         * @param {number} amount - Amount
         * @param {string} currency - Currency code (default: 'USD')
         * @param {string} locale - Locale (default: 'en-US')
         * @returns {string} Formatted currency
         */
        formatCurrency(amount, currency = 'USD', locale = 'en-US') {
            return new Intl.NumberFormat(locale, {
                style: 'currency',
                currency: currency
            }).format(amount);
        },
        
        /**
         * Format date
         * @param {Date|string|number} date - Date to format
         * @param {string} format - Format string (default: 'YYYY-MM-DD')
         * @returns {string} Formatted date
         */
        formatDate(date, format = 'YYYY-MM-DD') {
            const d = new Date(date);
            if (isNaN(d.getTime())) return '';
            
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            const hours = String(d.getHours()).padStart(2, '0');
            const minutes = String(d.getMinutes()).padStart(2, '0');
            const seconds = String(d.getSeconds()).padStart(2, '0');
            
            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day)
                .replace('HH', hours)
                .replace('mm', minutes)
                .replace('ss', seconds);
        },
        
        /**
         * Format file size
         * @param {number} bytes - Size in bytes
         * @returns {string} Formatted size
         */
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        
        /**
         * Parse query string to object
         * @param {string} queryString - Query string
         * @returns {Object} Parsed query parameters
         */
        parseQueryString(queryString) {
            const params = {};
            const query = queryString.startsWith('?') ? queryString.slice(1) : queryString;
            
            query.split('&').forEach(param => {
                const [key, value] = param.split('=');
                if (key) {
                    params[decodeURIComponent(key)] = decodeURIComponent(value || '');
                }
            });
            
            return params;
        },
        
        /**
         * Convert object to query string
         * @param {Object} obj - Object to convert
         * @returns {string} Query string
         */
        toQueryString(obj) {
            return Object.keys(obj)
                .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key])}`)
                .join('&');
        }
    },
    
    // Number Utilities
    number: {
        /**
         * Generate random number in range
         * @param {number} min - Minimum value
         * @param {number} max - Maximum value
         * @returns {number} Random number
         */
        random(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        },
        
        /**
         * Round number to specified decimals
         * @param {number} num - Number to round
         * @param {number} decimals - Number of decimal places
         * @returns {number} Rounded number
         */
        round(num, decimals = 2) {
            const factor = Math.pow(10, decimals);
            return Math.round(num * factor) / factor;
        },
        
        /**
         * Format number with thousand separators
         * @param {number} num - Number to format
         * @param {number} decimals - Decimal places
         * @returns {string} Formatted number
         */
        format(num, decimals = 2) {
            return num.toLocaleString(undefined, {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });
        },
        
        /**
         * Calculate percentage
         * @param {number} value - Current value
         * @param {number} total - Total value
         * @param {number} decimals - Decimal places
         * @returns {number} Percentage
         */
        percentage(value, total, decimals = 1) {
            if (total === 0) return 0;
            return this.round((value / total) * 100, decimals);
        },
        
        /**
         * Clamp number between min and max
         * @param {number} num - Number to clamp
         * @param {number} min - Minimum value
         * @param {number} max - Maximum value
         * @returns {number} Clamped number
         */
        clamp(num, min, max) {
            return Math.min(Math.max(num, min), max);
        },
        
        /**
         * Check if number is within range
         * @param {number} num - Number to check
         * @param {number} min - Minimum value
         * @param {number} max - Maximum value
         * @returns {boolean} True if within range
         */
        inRange(num, min, max) {
            return num >= min && num <= max;
        },
        
        /**
         * Calculate average of numbers
         * @param {...number} numbers - Numbers to average
         * @returns {number} Average
         */
        average(...numbers) {
            if (numbers.length === 0) return 0;
            const sum = numbers.reduce((a, b) => a + b, 0);
            return sum / numbers.length;
        },
        
        /**
         * Calculate sum of numbers
         * @param {...number} numbers - Numbers to sum
         * @returns {number} Sum
         */
        sum(...numbers) {
            return numbers.reduce((a, b) => a + b, 0);
        }
    },
    
    // Date Utilities
    date: {
        /**
         * Get current date in YYYY-MM-DD format
         * @returns {string} Current date
         */
        today() {
            return this.formatDate(new Date());
        },
        
        /**
         * Get yesterday's date
         * @returns {Date} Yesterday's date
         */
        yesterday() {
            const date = new Date();
            date.setDate(date.getDate() - 1);
            return date;
        },
        
        /**
         * Get tomorrow's date
         * @returns {Date} Tomorrow's date
         */
        tomorrow() {
            const date = new Date();
            date.setDate(date.getDate() + 1);
            return date;
        },
        
        /**
         * Format date
         * @param {Date} date - Date to format
         * @param {string} format - Format string
         * @returns {string} Formatted date
         */
        formatDate(date, format = 'YYYY-MM-DD') {
            return XpertFarmerUtils.string.formatDate(date, format);
        },
        
        /**
         * Parse date string
         * @param {string} dateString - Date string
         * @returns {Date} Parsed date
         */
        parseDate(dateString) {
            const date = new Date(dateString);
            return isNaN(date.getTime()) ? null : date;
        },
        
        /**
         * Add days to date
         * @param {Date} date - Start date
         * @param {number} days - Number of days to add
         * @returns {Date} New date
         */
        addDays(date, days) {
            const newDate = new Date(date);
            newDate.setDate(newDate.getDate() + days);
            return newDate;
        },
        
        /**
         * Add months to date
         * @param {Date} date - Start date
         * @param {number} months - Number of months to add
         * @returns {Date} New date
         */
        addMonths(date, months) {
            const newDate = new Date(date);
            newDate.setMonth(newDate.getMonth() + months);
            return newDate;
        },
        
        /**
         * Add years to date
         * @param {Date} date - Start date
         * @param {number} years - Number of years to add
         * @returns {Date} New date
         */
        addYears(date, years) {
            const newDate = new Date(date);
            newDate.setFullYear(newDate.getFullYear() + years);
            return newDate;
        },
        
        /**
         * Get difference between dates in days
         * @param {Date} date1 - First date
         * @param {Date} date2 - Second date
         * @returns {number} Difference in days
         */
        differenceInDays(date1, date2) {
            const diff = Math.abs(date1 - date2);
            return Math.floor(diff / (1000 * 60 * 60 * 24));
        },
        
        /**
         * Check if date is valid
         * @param {Date} date - Date to check
         * @returns {boolean} True if valid
         */
        isValid(date) {
            return date instanceof Date && !isNaN(date.getTime());
        },
        
        /**
         * Get start of month
         * @param {Date} date - Date
         * @returns {Date} Start of month
         */
        startOfMonth(date) {
            return new Date(date.getFullYear(), date.getMonth(), 1);
        },
        
        /**
         * Get end of month
         * @param {Date} date - Date
         * @returns {Date} End of month
         */
        endOfMonth(date) {
            return new Date(date.getFullYear(), date.getMonth() + 1, 0);
        },
        
        /**
         * Get start of year
         * @param {Date} date - Date
         * @returns {Date} Start of year
         */
        startOfYear(date) {
            return new Date(date.getFullYear(), 0, 1);
        },
        
        /**
         * Get end of year
         * @param {Date} date - Date
         * @returns {Date} End of year
         */
        endOfYear(date) {
            return new Date(date.getFullYear(), 11, 31);
        },
        
        /**
         * Get age from birth date
         * @param {Date} birthDate - Birth date
         * @returns {number} Age in years
         */
        getAge(birthDate) {
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            
            return age;
        },
        
        /**
         * Check if date is today
         * @param {Date} date - Date to check
         * @returns {boolean} True if today
         */
        isToday(date) {
            const today = new Date();
            return date.getDate() === today.getDate() &&
                   date.getMonth() === today.getMonth() &&
                   date.getFullYear() === today.getFullYear();
        },
        
        /**
         * Check if date is in the past
         * @param {Date} date - Date to check
         * @returns {boolean} True if in past
         */
        isPast(date) {
            return date < new Date();
        },
        
        /**
         * Check if date is in the future
         * @param {Date} date - Date to check
         * @returns {boolean} True if in future
         */
        isFuture(date) {
            return date > new Date();
        }
    },
    
    // Array Utilities
    array: {
        /**
         * Remove duplicates from array
         * @param {Array} array - Input array
         * @returns {Array} Array without duplicates
         */
        unique(array) {
            return [...new Set(array)];
        },
        
        /**
         * Shuffle array (Fisher-Yates algorithm)
         * @param {Array} array - Array to shuffle
         * @returns {Array} Shuffled array
         */
        shuffle(array) {
            const newArray = [...array];
            for (let i = newArray.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
            }
            return newArray;
        },
        
        /**
         * Sort array by property
         * @param {Array} array - Array to sort
         * @param {string} property - Property to sort by
         * @param {boolean} ascending - Sort direction
         * @returns {Array} Sorted array
         */
        sortBy(array, property, ascending = true) {
            return [...array].sort((a, b) => {
                const aValue = a[property];
                const bValue = b[property];
                
                if (aValue < bValue) return ascending ? -1 : 1;
                if (aValue > bValue) return ascending ? 1 : -1;
                return 0;
            });
        },
        
        /**
         * Group array by property
         * @param {Array} array - Array to group
         * @param {string} property - Property to group by
         * @returns {Object} Grouped object
         */
        groupBy(array, property) {
            return array.reduce((groups, item) => {
                const key = item[property];
                if (!groups[key]) {
                    groups[key] = [];
                }
                groups[key].push(item);
                return groups;
            }, {});
        },
        
        /**
         * Chunk array into smaller arrays
         * @param {Array} array - Array to chunk
         * @param {number} size - Chunk size
         * @returns {Array} Array of chunks
         */
        chunk(array, size) {
            const chunks = [];
            for (let i = 0; i < array.length; i += size) {
                chunks.push(array.slice(i, i + size));
            }
            return chunks;
        },
        
        /**
         * Flatten nested array
         * @param {Array} array - Array to flatten
         * @returns {Array} Flattened array
         */
        flatten(array) {
            return array.reduce((flat, item) => {
                return flat.concat(Array.isArray(item) ? this.flatten(item) : item);
            }, []);
        },
        
        /**
         * Find object in array by property value
         * @param {Array} array - Array to search
         * @param {string} property - Property name
         * @param {*} value - Property value
         * @returns {Object|null} Found object or null
         */
        findBy(array, property, value) {
            return array.find(item => item[property] === value) || null;
        },
        
        /**
         * Filter array by multiple criteria
         * @param {Array} array - Array to filter
         * @param {Object} criteria - Filter criteria
         * @returns {Array} Filtered array
         */
        filterBy(array, criteria) {
            return array.filter(item => {
                return Object.keys(criteria).every(key => {
                    if (typeof criteria[key] === 'function') {
                        return criteria[key](item[key]);
                    }
                    return item[key] === criteria[key];
                });
            });
        },
        
        /**
         * Map array and remove null/undefined values
         * @param {Array} array - Array to map
         * @param {Function} mapper - Mapping function
         * @returns {Array} Mapped array without nulls
         */
        compactMap(array, mapper) {
            return array.map(mapper).filter(item => item != null);
        },
        
        /**
         * Get random item from array
         * @param {Array} array - Array
         * @returns {*} Random item
         */
        randomItem(array) {
            return array[Math.floor(Math.random() * array.length)];
        },
        
        /**
         * Create range array
         * @param {number} start - Start number
         * @param {number} end - End number
         * @param {number} step - Step size
         * @returns {Array} Range array
         */
        range(start, end, step = 1) {
            const array = [];
            for (let i = start; i <= end; i += step) {
                array.push(i);
            }
            return array;
        }
    },
    
    // Object Utilities
    object: {
        /**
         * Deep clone object
         * @param {Object} obj - Object to clone
         * @returns {Object} Cloned object
         */
        clone(obj) {
            return JSON.parse(JSON.stringify(obj));
        },
        
        /**
         * Merge multiple objects
         * @param {...Object} objects - Objects to merge
         * @returns {Object} Merged object
         */
        merge(...objects) {
            return Object.assign({}, ...objects);
        },
        
        /**
         * Deep merge objects
         * @param {Object} target - Target object
         * @param {...Object} sources - Source objects
         * @returns {Object} Deep merged object
         */
        deepMerge(target, ...sources) {
            if (!sources.length) return target;
            const source = sources.shift();
            
            if (this.isObject(target) && this.isObject(source)) {
                for (const key in source) {
                    if (this.isObject(source[key])) {
                        if (!target[key]) Object.assign(target, { [key]: {} });
                        this.deepMerge(target[key], source[key]);
                    } else {
                        Object.assign(target, { [key]: source[key] });
                    }
                }
            }
            
            return this.deepMerge(target, ...sources);
        },
        
        /**
         * Check if value is plain object
         * @param {*} value - Value to check
         * @returns {boolean} True if plain object
         */
        isObject(value) {
            return value && typeof value === 'object' && !Array.isArray(value);
        },
        
        /**
         * Get object keys as array
         * @param {Object} obj - Object
         * @returns {Array} Array of keys
         */
        keys(obj) {
            return Object.keys(obj);
        },
        
        /**
         * Get object values as array
         * @param {Object} obj - Object
         * @returns {Array} Array of values
         */
        values(obj) {
            return Object.values(obj);
        },
        
        /**
         * Filter object by predicate
         * @param {Object} obj - Object to filter
         * @param {Function} predicate - Filter function
         * @returns {Object} Filtered object
         */
        filter(obj, predicate) {
            return Object.keys(obj)
                .filter(key => predicate(obj[key], key))
                .reduce((result, key) => {
                    result[key] = obj[key];
                    return result;
                }, {});
        },
        
        /**
         * Map object values
         * @param {Object} obj - Object to map
         * @param {Function} mapper - Mapping function
         * @returns {Object} Mapped object
         */
        map(obj, mapper) {
            return Object.keys(obj).reduce((result, key) => {
                result[key] = mapper(obj[key], key);
                return result;
            }, {});
        },
        
        /**
         * Pick specific properties from object
         * @param {Object} obj - Source object
         * @param {...string} keys - Keys to pick
         * @returns {Object} Object with picked properties
         */
        pick(obj, ...keys) {
            return keys.reduce((result, key) => {
                if (obj.hasOwnProperty(key)) {
                    result[key] = obj[key];
                }
                return result;
            }, {});
        },
        
        /**
         * Omit specific properties from object
         * @param {Object} obj - Source object
         * @param {...string} keys - Keys to omit
         * @returns {Object} Object without omitted properties
         */
        omit(obj, ...keys) {
            const result = { ...obj };
            keys.forEach(key => delete result[key]);
            return result;
        },
        
        /**
         * Check if object is empty
         * @param {Object} obj - Object to check
         * @returns {boolean} True if empty
         */
        isEmpty(obj) {
            return Object.keys(obj).length === 0;
        },
        
        /**
         * Get nested property value
         * @param {Object} obj - Object
         * @param {string} path - Property path
         * @param {*} defaultValue - Default value
         * @returns {*} Property value or default
         */
        get(obj, path, defaultValue = undefined) {
            const keys = path.split('.');
            let result = obj;
            
            for (const key of keys) {
                if (result && typeof result === 'object' && key in result) {
                    result = result[key];
                } else {
                    return defaultValue;
                }
            }
            
            return result;
        },
        
        /**
         * Set nested property value
         * @param {Object} obj - Object
         * @param {string} path - Property path
         * @param {*} value - Value to set
         * @returns {Object} Updated object
         */
        set(obj, path, value) {
            const keys = path.split('.');
            let current = obj;
            
            for (let i = 0; i < keys.length - 1; i++) {
                const key = keys[i];
                if (!current[key] || typeof current[key] !== 'object') {
                    current[key] = {};
                }
                current = current[key];
            }
            
            current[keys[keys.length - 1]] = value;
            return obj;
        }
    },
    
    // Browser Utilities
    browser: {
        /**
         * Get browser information
         * @returns {Object} Browser info
         */
        getInfo() {
            const ua = navigator.userAgent;
            let browser = 'Unknown';
            let version = '';
            
            // Detect browser
            if (ua.indexOf('Firefox') > -1) {
                browser = 'Firefox';
                version = ua.match(/Firefox\/(\d+)/)?.[1] || '';
            } else if (ua.indexOf('Chrome') > -1 && ua.indexOf('Edg') === -1) {
                browser = 'Chrome';
                version = ua.match(/Chrome\/(\d+)/)?.[1] || '';
            } else if (ua.indexOf('Safari') > -1 && ua.indexOf('Chrome') === -1) {
                browser = 'Safari';
                version = ua.match(/Version\/(\d+)/)?.[1] || '';
            } else if (ua.indexOf('Edg') > -1) {
                browser = 'Edge';
                version = ua.match(/Edg\/(\d+)/)?.[1] || '';
            }
            
            return {
                browser,
                version,
                userAgent: ua,
                language: navigator.language,
                platform: navigator.platform,
                isMobile: /Mobi|Android/i.test(ua),
                isTablet: /Tablet|iPad/i.test(ua)
            };
        },
        
        /**
         * Check if browser supports feature
         * @param {string} feature - Feature to check
         * @returns {boolean} True if supported
         */
        supports(feature) {
            const features = {
                localStorage: 'localStorage' in window,
                sessionStorage: 'sessionStorage' in window,
                geolocation: 'geolocation' in navigator,
                touch: 'ontouchstart' in window,
                serviceWorker: 'serviceWorker' in navigator,
                pushManager: 'pushManager' in window,
                webWorker: 'Worker' in window,
                webGL: 'WebGLRenderingContext' in window,
                webAudio: 'AudioContext' in window || 'webkitAudioContext' in window
            };
            
            return features[feature] || false;
        },
        
        /**
         * Get query parameter value
         * @param {string} name - Parameter name
         * @returns {string|null} Parameter value
         */
        getQueryParam(name) {
            const params = new URLSearchParams(window.location.search);
            return params.get(name);
        },
        
        /**
         * Set query parameter
         * @param {string} name - Parameter name
         * @param {string} value - Parameter value
         */
        setQueryParam(name, value) {
            const url = new URL(window.location);
            url.searchParams.set(name, value);
            window.history.pushState({}, '', url);
        },
        
        /**
         * Remove query parameter
         * @param {string} name - Parameter name
         */
        removeQueryParam(name) {
            const url = new URL(window.location);
            url.searchParams.delete(name);
            window.history.pushState({}, '', url);
        },
        
        /**
         * Copy text to clipboard
         * @param {string} text - Text to copy
         * @returns {Promise} Promise that resolves when copied
         */
        copyToClipboard(text) {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                return navigator.clipboard.writeText(text);
            } else {
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                
                try {
                    document.execCommand('copy');
                    return Promise.resolve();
                } catch (err) {
                    return Promise.reject(err);
                } finally {
                    document.body.removeChild(textarea);
                }
            }
        },
        
        /**
         * Download file
         * @param {string} data - File data
         * @param {string} filename - File name
         * @param {string} type - MIME type
         */
        downloadFile(data, filename, type = 'text/plain') {
            const blob = new Blob([data], { type });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        },
        
        /**
         * Read file as text
         * @param {File} file - File to read
         * @returns {Promise<string>} Promise with file content
         */
        readFileAsText(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.onerror = () => reject(reader.error);
                reader.readAsText(file);
            });
        },
        
        /**
         * Read file as data URL
         * @param {File} file - File to read
         * @returns {Promise<string>} Promise with data URL
         */
        readFileAsDataURL(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.onerror = () => reject(reader.error);
                reader.readAsDataURL(file);
            });
        },
        
        /**
         * Get device pixel ratio
         * @returns {number} Pixel ratio
         */
        getPixelRatio() {
            return window.devicePixelRatio || 1;
        },
        
        /**
         * Check if device is online
         * @returns {boolean} True if online
         */
        isOnline() {
            return navigator.onLine;
        },
        
        /**
         * Add online/offline event listeners
         * @param {Function} onlineCallback - Online callback
         * @param {Function} offlineCallback - Offline callback
         */
        onConnectionChange(onlineCallback, offlineCallback) {
            window.addEventListener('online', onlineCallback);
            window.addEventListener('offline', offlineCallback);
        }
    },
    
    // Storage Utilities
    storage: {
        /**
         * Set item in localStorage with expiration
         * @param {string} key - Storage key
         * @param {*} value - Value to store
         * @param {number} ttl - Time to live in seconds
         */
        setWithExpiry(key, value, ttl) {
            const item = {
                value: value,
                expiry: Date.now() + (ttl * 1000)
            };
            localStorage.setItem(key, JSON.stringify(item));
        },
        
        /**
         * Get item from localStorage with expiration
         * @param {string} key - Storage key
         * @returns {*} Stored value or null if expired
         */
        getWithExpiry(key) {
            const itemStr = localStorage.getItem(key);
            if (!itemStr) return null;
            
            const item = JSON.parse(itemStr);
            if (Date.now() > item.expiry) {
                localStorage.removeItem(key);
                return null;
            }
            
            return item.value;
        },
        
        /**
         * Clear expired items from localStorage
         */
        clearExpired() {
            const now = Date.now();
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                try {
                    const item = JSON.parse(localStorage.getItem(key));
                    if (item && item.expiry && now > item.expiry) {
                        localStorage.removeItem(key);
                        i--; // Adjust index after removal
                    }
                } catch (e) {
                    // Not a JSON item, skip
                }
            }
        },
        
        /**
         * Get all keys with prefix
         * @param {string} prefix - Key prefix
         * @returns {Array} Array of keys
         */
        getKeysWithPrefix(prefix) {
            const keys = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith(prefix)) {
                    keys.push(key);
                }
            }
            return keys;
        },
        
        /**
         * Remove all items with prefix
         * @param {string} prefix - Key prefix
         */
        removeWithPrefix(prefix) {
            this.getKeysWithPrefix(prefix).forEach(key => {
                localStorage.removeItem(key);
            });
        },
        
        /**
         * Check if storage is available
         * @param {string} type - Storage type ('localStorage' or 'sessionStorage')
         * @returns {boolean} True if available
         */
        isAvailable(type = 'localStorage') {
            try {
                const storage = window[type];
                const testKey = '__test__';
                storage.setItem(testKey, testKey);
                storage.removeItem(testKey);
                return true;
            } catch (e) {
                return false;
            }
        },
        
        /**
         * Get storage usage
         * @returns {Object} Storage usage info
         */
        getUsage() {
            let total = 0;
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                const value = localStorage.getItem(key);
                total += key.length + value.length;
            }
            
            return {
                items: localStorage.length,
                size: total,
                sizeFormatted: XpertFarmerUtils.string.formatFileSize(total * 2), // Approximate byte size
                quota: 5 * 1024 * 1024, // 5MB typical quota
                percentage: Math.min((total * 2) / (5 * 1024 * 1024) * 100, 100)
            };
        }
    },
    
    // Validation Utilities
    validation: {
        /**
         * Check if value is empty
         * @param {*} value - Value to check
         * @returns {boolean} True if empty
         */
        isEmpty(value) {
            if (value === null || value === undefined) return true;
            if (typeof value === 'string') return value.trim() === '';
            if (Array.isArray(value)) return value.length === 0;
            if (typeof value === 'object') return Object.keys(value).length === 0;
            return false;
        },
        
        /**
         * Check if value is email
         * @param {string} email - Email to check
         * @returns {boolean} True if valid email
         */
        isEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },
        
        /**
         * Check if value is phone number
         * @param {string} phone - Phone number to check
         * @returns {boolean} True if valid phone
         */
        isPhone(phone) {
            const re = /^[\+]?[1-9][\d]{0,15}$/;
            return re.test(phone.replace(/[\s\-\(\)\.]/g, ''));
        },
        
        /**
         * Check if value is URL
         * @param {string} url - URL to check
         * @returns {boolean} True if valid URL
         */
        isUrl(url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        },
        
        /**
         * Check if value is date
         * @param {string} dateString - Date string to check
         * @returns {boolean} True if valid date
         */
        isDate(dateString) {
            const date = new Date(dateString);
            return date instanceof Date && !isNaN(date.getTime());
        },
        
        /**
         * Check if value is number
         * @param {*} value - Value to check
         * @returns {boolean} True if number
         */
        isNumber(value) {
            return !isNaN(parseFloat(value)) && isFinite(value);
        },
        
        /**
         * Check if value is integer
         * @param {*} value - Value to check
         * @returns {boolean} True if integer
         */
        isInteger(value) {
            return Number.isInteger(Number(value));
        },
        
        /**
         * Check if value is between min and max
         * @param {number} value - Value to check
         * @param {number} min - Minimum value
         * @param {number} max - Maximum value
         * @returns {boolean} True if in range
         */
        isBetween(value, min, max) {
            const num = Number(value);
            return !isNaN(num) && num >= min && num <= max;
        },
        
        /**
         * Check if value matches pattern
         * @param {string} value - Value to check
         * @param {string|RegExp} pattern - Pattern to match
         * @returns {boolean} True if matches
         */
        matches(value, pattern) {
            if (typeof pattern === 'string') {
                pattern = new RegExp(pattern);
            }
            return pattern.test(value);
        },
        
        /**
         * Check if value has minimum length
         * @param {string|Array} value - Value to check
         * @param {number} min - Minimum length
         * @returns {boolean} True if meets minimum length
         */
        hasMinLength(value, min) {
            if (typeof value === 'string') {
                return value.length >= min;
            }
            if (Array.isArray(value)) {
                return value.length >= min;
            }
            return false;
        },
        
        /**
         * Check if value has maximum length
         * @param {string|Array} value - Value to check
         * @param {number} max - Maximum length
         * @returns {boolean} True if meets maximum length
         */
        hasMaxLength(value, max) {
            if (typeof value === 'string') {
                return value.length <= max;
            }
            if (Array.isArray(value)) {
                return value.length <= max;
            }
            return false;
        },
        
        /**
         * Validate object against schema
         * @param {Object} obj - Object to validate
         * @param {Object} schema - Validation schema
         * @returns {Object} Validation result
         */
        validateSchema(obj, schema) {
            const errors = {};
            
            Object.keys(schema).forEach(key => {
                const rules = schema[key];
                const value = obj[key];
                
                if (rules.required && this.isEmpty(value)) {
                    errors[key] = rules.requiredMessage || `${key} is required`;
                    return;
                }
                
                if (!this.isEmpty(value)) {
                    if (rules.type && typeof value !== rules.type) {
                        errors[key] = rules.typeMessage || `${key} must be ${rules.type}`;
                    }
                    
                    if (rules.min && value < rules.min) {
                        errors[key] = rules.minMessage || `${key} must be at least ${rules.min}`;
                    }
                    
                    if (rules.max && value > rules.max) {
                        errors[key] = rules.maxMessage || `${key} must be at most ${rules.max}`;
                    }
                    
                    if (rules.minLength && !this.hasMinLength(value, rules.minLength)) {
                        errors[key] = rules.minLengthMessage || 
                            `${key} must be at least ${rules.minLength} characters`;
                    }
                    
                    if (rules.maxLength && !this.hasMaxLength(value, rules.maxLength)) {
                        errors[key] = rules.maxLengthMessage || 
                            `${key} must be at most ${rules.maxLength} characters`;
                    }
                    
                    if (rules.pattern && !this.matches(value, rules.pattern)) {
                        errors[key] = rules.patternMessage || `${key} is invalid`;
                    }
                    
                    if (rules.validate && !rules.validate(value)) {
                        errors[key] = rules.validateMessage || `${key} is invalid`;
                    }
                }
            });
            
            return {
                isValid: Object.keys(errors).length === 0,
                errors: errors
            };
        }
    },
    
    // Performance Utilities
    performance: {
        /**
         * Measure function execution time
         * @param {Function} fn - Function to measure
         * @param {...*} args - Function arguments
         * @returns {Object} Measurement result
         */
        measure(fn, ...args) {
            const start = performance.now();
            const result = fn(...args);
            const end = performance.now();
            
            return {
                result: result,
                time: end - start,
                timeFormatted: `${(end - start).toFixed(2)}ms`
            };
        },
        
        /**
         * Debounce function
         * @param {Function} fn - Function to debounce
         * @param {number} delay - Delay in milliseconds
         * @returns {Function} Debounced function
         */
        debounce(fn, delay) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => fn.apply(this, args), delay);
            };
        },
        
        /**
         * Throttle function
         * @param {Function} fn - Function to throttle
         * @param {number} limit - Time limit in milliseconds
         * @returns {Function} Throttled function
         */
        throttle(fn, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    fn.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },
        
        /**
         * Memoize function
         * @param {Function} fn - Function to memoize
         * @returns {Function} Memoized function
         */
        memoize(fn) {
            const cache = new Map();
            return function(...args) {
                const key = JSON.stringify(args);
                if (cache.has(key)) {
                    return cache.get(key);
                }
                const result = fn.apply(this, args);
                cache.set(key, result);
                return result;
            };
        },
        
        /**
         * Create animation frame loop
         * @param {Function} callback - Callback function
         * @returns {Object} Loop controller
         */
        createAnimationLoop(callback) {
            let animationId;
            let running = false;
            
            const loop = () => {
                if (running) {
                    callback();
                    animationId = requestAnimationFrame(loop);
                }
            };
            
            return {
                start() {
                    if (!running) {
                        running = true;
                        loop();
                    }
                },
                stop() {
                    running = false;
                    if (animationId) {
                        cancelAnimationFrame(animationId);
                    }
                },
                isRunning() {
                    return running;
                }
            };
        },
        
        /**
         * Get memory usage (if supported)
         * @returns {Object|null} Memory info or null
         */
        getMemoryInfo() {
            if (performance.memory) {
                return {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit,
                    percentage: (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100
                };
            }
            return null;
        }
    },
    
    // Color Utilities
    color: {
        /**
         * Convert hex to RGB
         * @param {string} hex - Hex color
         * @returns {Object} RGB values
         */
        hexToRgb(hex) {
            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        },
        
        /**
         * Convert RGB to hex
         * @param {number} r - Red value (0-255)
         * @param {number} g - Green value (0-255)
         * @param {number} b - Blue value (0-255)
         * @returns {string} Hex color
         */
        rgbToHex(r, g, b) {
            return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
        },
        
        /**
         * Convert hex to RGBA
         * @param {string} hex - Hex color
         * @param {number} alpha - Alpha value (0-1)
         * @returns {string} RGBA color
         */
        hexToRgba(hex, alpha = 1) {
            const rgb = this.hexToRgb(hex);
            if (!rgb) return hex;
            return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
        },
        
        /**
         * Lighten color
         * @param {string} hex - Hex color
         * @param {number} percent - Lighten percentage
         * @returns {string} Lightened hex color
         */
        lighten(hex, percent) {
            const rgb = this.hexToRgb(hex);
            if (!rgb) return hex;
            
            const factor = 1 + (percent / 100);
            rgb.r = Math.min(255, Math.round(rgb.r * factor));
            rgb.g = Math.min(255, Math.round(rgb.g * factor));
            rgb.b = Math.min(255, Math.round(rgb.b * factor));
            
            return this.rgbToHex(rgb.r, rgb.g, rgb.b);
        },
        
        /**
         * Darken color
         * @param {string} hex - Hex color
         * @param {number} percent - Darken percentage
         * @returns {string} Darkened hex color
         */
        darken(hex, percent) {
            const rgb = this.hexToRgb(hex);
            if (!rgb) return hex;
            
            const factor = 1 - (percent / 100);
            rgb.r = Math.max(0, Math.round(rgb.r * factor));
            rgb.g = Math.max(0, Math.round(rgb.g * factor));
            rgb.b = Math.max(0, Math.round(rgb.b * factor));
            
            return this.rgbToHex(rgb.r, rgb.g, rgb.b);
        },
        
        /**
         * Check if color is light
         * @param {string} hex - Hex color
         * @returns {boolean} True if light color
         */
        isLight(hex) {
            const rgb = this.hexToRgb(hex);
            if (!rgb) return false;
            
            // Calculate relative luminance
            const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
            return luminance > 0.5;
        },
 /**
 * Get contrast color (black or white)
 * @param {string} hex - Hex color
 * @returns {string} '#000000' or '#ffffff'
 */
getContrastColor(hex) {
    return this.isLight(hex) ? '#000000' : '#ffffff';
},

/**
 * Generate random color
 * @returns {string} Random hex color
 */
random() {
    return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
},

/**
 * Generate color gradient
 * @param {string} startColor - Start hex color
 * @param {string} endColor - End hex color
 * @param {number} steps - Number of gradient steps
 * @returns {Array} Array of hex colors
 */
generateGradient(startColor, endColor, steps) {
    const start = this.hexToRgb(startColor);
    const end = this.hexToRgb(endColor);
    if (!start || !end) return [];

    const gradient = [];
    for (let i = 0; i < steps; i++) {
        const r = Math.round(start.r + (end.r - start.r) * (i / (steps - 1)));
        const g = Math.round(start.g + (end.g - start.g) * (i / (steps - 1)));
        const b = Math.round(start.b + (end.b - start.b) * (i / (steps - 1)));
        gradient.push(this.rgbToHex(r, g, b));
    }

    return gradient;
}
},

// Event Utilities
event: {
    /**
     * Add event listener with options
     * @param {HTMLElement} element - Target element
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     * @param {Object} options - Event options
     * @returns {Function} Function to remove listener
     */
    on(element, event, handler, options = {}) {
        element.addEventListener(event, handler, options);
        return () => element.removeEventListener(event, handler, options);
    },

    /**
     * Add one-time event listener
     * @param {HTMLElement} element - Target element
     * @param {string} event - Event name
     * @param {Function} handler - Event handler
     * @returns {Function} Function to remove listener
     */
    once(element, event, handler) {
        const onceHandler = (e) => {
            handler(e);
            element.removeEventListener(event, onceHandler);
        };
        return this.on(element, event, onceHandler);
    },

    /**
     * Trigger custom event
     * @param {HTMLElement} element - Target element
     * @param {string} eventName - Event name
     * @param {Object} detail - Event detail data
     * @param {Object} options - Event options
     */
    trigger(element, eventName, detail = {}, options = {}) {
        const event = new CustomEvent(eventName, {
            bubbles: true,
            cancelable: true,
            detail,
            ...options
        });
        element.dispatchEvent(event);
    },

    /**
     * Prevent default and stop propagation
     * @param {Event} event - Event object
     */
    stop(event) {
        event.preventDefault();
        event.stopPropagation();
    },

    /**
     * Get event target or closest selector
     * @param {Event} event - Event object
     * @param {string} selector - CSS selector
     * @returns {HTMLElement|null} Target element
     */
    getTarget(event, selector = null) {
        if (!selector) return event.target;
        return event.target.closest(selector);
    }
},

// Initialization
init() {
    this.storage.clearExpired();
    this.setupPerformanceMonitoring();
    this.setupErrorHandling();
    console.log('Xpert Farmer IMS Utilities Initialized');
},

/**
 * Setup performance monitoring
 */
setupPerformanceMonitoring() {
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.duration > 50) {
                    console.warn('Long task detected:', entry);
                }
            }
        });

        observer.observe({ entryTypes: ['longtask'] });
    }
},

/**
 * Setup error handling
 */
setupErrorHandling() {
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
    });

    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
    });
}
};

// Initialize utilities
document.addEventListener('DOMContentLoaded', () => {
    XpertFarmerUtils.init();
});

// Make utilities available globally
window.XpertFarmerUtils = XpertFarmerUtils;
