// API Configuration
const API_BASE_URL = 'http://localhost:8010/api';

// API Helper Functions
class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error('API Error:', errorData);
                let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
                if (errorData.detail) {
                    if (Array.isArray(errorData.detail)) {
                        errorMsg = errorData.detail.map(err => err.msg || err).join(', ');
                    } else {
                        errorMsg = errorData.detail;
                    }
                }
                throw new Error(errorMsg);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Dashboard APIs
    static async getDashboardStats(collegeFilter = null) {
        const timestamp = Date.now();
        const url = collegeFilter ? `/dashboard/stats?college_filter=${collegeFilter}&_t=${timestamp}` : `/dashboard/stats?_t=${timestamp}`;
        return this.request(url);
    }

    static async getAlerts(collegeFilter = null) {
        const timestamp = Date.now();
        const url = collegeFilter ? `/dashboard/alerts?college_filter=${collegeFilter}&_t=${timestamp}` : `/dashboard/alerts?_t=${timestamp}`;
        return this.request(url);
    }

    // Students APIs
    static async getStudents(params = {}) {
        params._t = Date.now(); // Prevent caching
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/students?${queryString}`);
    }

    static async getStudent(studentId) {
        return this.request(`/student/${studentId}`);
    }

    static async updateStudent(studentId, updates) {
        return this.request(`/student/${studentId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    }

    static async getHighRiskStudents() {
        return this.request('/students/high-risk');
    }

    static async getDepartments() {
        return this.request('/students/departments');
    }

    // Upload APIs
    static async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        return this.request('/upload-file', {
            method: 'POST',
            headers: {}, // Remove Content-Type to let browser set it for FormData
            body: formData
        });
    }

    static async processData(mappings, sessionId, file) {
        console.log('Processing data with:', { mappings, sessionId, fileName: file.name });
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('mappings', JSON.stringify(mappings));
        formData.append('session_id', sessionId);
        
        // Log what we're sending
        for (let [key, value] of formData.entries()) {
            console.log('FormData:', key, value);
        }

        // Direct fetch call instead of using this.request
        const url = `${API_BASE_URL}/process-data`;
        console.log('Sending to:', url);
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('API Error:', errorData);
            let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
            if (errorData.detail) {
                if (Array.isArray(errorData.detail)) {
                    errorMsg = errorData.detail.map(err => err.msg || err).join(', ');
                } else {
                    errorMsg = errorData.detail;
                }
            }
            throw new Error(errorMsg);
        }
        
        return await response.json();
    }

    static async getSampleFormat() {
        return this.request('/sample-format');
    }
}

// Utility Functions
class Utils {
    static showLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.classList.add('active');
        }
    }

    static hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.classList.remove('active');
        }
    }

    static showError(message, container = null) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.innerHTML = `
            <span class="alert-icon">⚠️</span>
            <span class="alert-message">${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
        `;

        if (container) {
            container.appendChild(errorDiv);
        } else {
            document.body.appendChild(errorDiv);
        }

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }

    static showSuccess(message, container = null) {
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success';
        successDiv.innerHTML = `
            <span class="alert-icon">✅</span>
            <span class="alert-message">${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
        `;

        if (container) {
            container.appendChild(successDiv);
        } else {
            document.body.appendChild(successDiv);
        }

        setTimeout(() => {
            if (successDiv.parentElement) {
                successDiv.remove();
            }
        }, 3000);
    }

    static formatNumber(num) {
        return new Intl.NumberFormat('en-IN').format(num);
    }

    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    }

    static getRiskBadgeClass(riskLevel) {
        const level = riskLevel.toLowerCase();
        return `risk-badge ${level}`;
    }

    static getRiskColor(riskLevel) {
        const colors = {
            'critical': '#dc2626',
            'high': '#ea580c',
            'medium': '#eab308',
            'low': '#16a34a'
        };
        return colors[riskLevel.toLowerCase()] || '#6b7280';
    }

    static debounce(func, wait) {
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

    static async downloadFile(data, filename, type = 'text/csv') {
        const blob = new Blob([data], { type });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    static validatePhone(phone) {
        const re = /^[6-9]\d{9}$/;
        return re.test(phone);
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    static formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static getInitials(name) {
        return name
            .split(' ')
            .map(word => word.charAt(0))
            .join('')
            .toUpperCase()
            .substring(0, 2);
    }

    static generateId() {
        return Math.random().toString(36).substr(2, 9);
    }

    static copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
        this.showSuccess('Copied to clipboard!');
    }
}

// Event Emitter for component communication
class EventEmitter {
    constructor() {
        this.events = {};
    }

    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }

    emit(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(data));
        }
    }

    off(event, callback) {
        if (this.events[event]) {
            this.events[event] = this.events[event].filter(cb => cb !== callback);
        }
    }
}

// Global event emitter instance
window.eventBus = new EventEmitter();

// Global error handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    Utils.showError('An unexpected error occurred. Please try again.');
});

// Export for use in other files
window.API = API;
window.Utils = Utils;