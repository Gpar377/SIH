// Alerts Page JavaScript
class AlertsManager {
    constructor() {
        this.alerts = [];
        this.filteredAlerts = [];
        this.currentStudent = null;
        this.alertHistory = [];
        
        this.init();
    }

    async init() {
        await this.loadAlerts();
        this.setupEventListeners();
        this.loadDepartments();
    }

    setupEventListeners() {
        // Filter dropdowns
        ['alert-priority-filter', 'alert-status-filter', 'alert-department-filter'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => {
                this.applyFilters();
            });
        });
    }

    async loadAlerts() {
        try {
            Utils.showLoading();
            
            // Get high-risk students and convert to alerts
            const response = await API.getStudents({ limit: 1000 });
            const students = response.students || response || [];
            
            // Generate alerts for high-risk students
            this.alerts = students
                .filter(student => ['Critical', 'High'].includes(student.risk_level))
                .map(student => ({
                    id: `alert_${student.student_id}`,
                    student_id: student.student_id,
                    student_name: student.name,
                    department: student.department,
                    priority: student.risk_level,
                    status: this.getRandomStatus(),
                    created_at: this.getRandomDate(),
                    risk_factors: this.generateRiskFactors(student),
                    contact_info: {
                        email: `${student.student_id}@student.edu.in`,
                        phone: `+91-${Math.floor(Math.random() * 9000000000) + 1000000000}`,
                        mentor: `mentor_${student.department.toLowerCase().replace(/\s+/g, '_')}@college.edu.in`
                    },
                    student_data: student
                }));

            this.filteredAlerts = [...this.alerts];
            this.renderAlerts();
            this.updateStatistics();
            
        } catch (error) {
            console.error('Error loading alerts:', error);
            Utils.showError('Failed to load alerts');
        } finally {
            Utils.hideLoading();
        }
    }

    generateRiskFactors(student) {
        const factors = [];
        
        if (student.attendance_percentage < 50) {
            factors.push(`Very low attendance: ${student.attendance_percentage}%`);
        } else if (student.attendance_percentage < 75) {
            factors.push(`Poor attendance: ${student.attendance_percentage}%`);
        }
        
        if (student.marks < 40) {
            factors.push(`Failing grades: ${student.marks}%`);
        } else if (student.marks < 60) {
            factors.push(`Low performance: ${student.marks}%`);
        }
        
        if (student.family_income < 200000) {
            factors.push('Financial constraints');
        }
        
        if (student.internet_access === 'No') {
            factors.push('No internet access');
        }
        
        if (student.electricity === 'No') {
            factors.push('No electricity access');
        }
        
        return factors.length > 0 ? factors : ['Multiple risk indicators detected'];
    }

    getRandomStatus() {
        const statuses = ['New', 'New', 'New', 'Contacted', 'Resolved'];
        return statuses[Math.floor(Math.random() * statuses.length)];
    }

    getRandomDate() {
        const now = new Date();
        const daysAgo = Math.floor(Math.random() * 7);
        const date = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
        return date.toISOString();
    }

    applyFilters() {
        const priorityFilter = document.getElementById('alert-priority-filter').value;
        const statusFilter = document.getElementById('alert-status-filter').value;
        const departmentFilter = document.getElementById('alert-department-filter').value;

        this.filteredAlerts = this.alerts.filter(alert => {
            const matchesPriority = !priorityFilter || alert.priority === priorityFilter;
            const matchesStatus = !statusFilter || alert.status === statusFilter;
            const matchesDepartment = !departmentFilter || alert.department === departmentFilter;

            return matchesPriority && matchesStatus && matchesDepartment;
        });

        this.renderAlerts();
        this.updateStatistics();
    }

    renderAlerts() {
        const criticalAlerts = this.filteredAlerts.filter(a => a.priority === 'Critical');
        const highAlerts = this.filteredAlerts.filter(a => a.priority === 'High');

        this.renderAlertSection('critical-alerts-container', criticalAlerts, 'critical');
        this.renderAlertSection('high-alerts-container', highAlerts, 'high');

        document.getElementById('critical-badge').textContent = criticalAlerts.length;
        document.getElementById('high-badge').textContent = highAlerts.length;
    }

    renderAlertSection(containerId, alerts, type) {
        const container = document.getElementById(containerId);
        
        if (alerts.length === 0) {
            container.innerHTML = `<div class="no-alerts">No ${type} alerts at this time.</div>`;
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="alert-card ${alert.priority.toLowerCase()} ${alert.status.toLowerCase()}">
                <div class="alert-header">
                    <div class="student-info">
                        <h4>${alert.student_name}</h4>
                        <p>${alert.student_id} • ${alert.department}</p>
                    </div>
                    <div class="alert-status">
                        <span class="status-badge ${alert.status.toLowerCase()}">${alert.status}</span>
                        <span class="priority-badge ${alert.priority.toLowerCase()}">${alert.priority}</span>
                    </div>
                </div>
                
                <div class="alert-body">
                    <div class="risk-factors">
                        <h5>Risk Factors:</h5>
                        <ul>
                            ${alert.risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="alert-meta">
                        <small>Created: ${new Date(alert.created_at).toLocaleDateString()}</small>
                    </div>
                </div>
                
                <div class="alert-actions">
                    ${alert.status === 'New' ? `
                        <button class="btn-primary btn-sm" onclick="alertsManager.contactStudent('${alert.id}')">
                            📞 Contact Student
                        </button>
                        <button class="btn-secondary btn-sm" onclick="alertsManager.viewStudent('${alert.student_id}')">
                            👁️ View Details
                        </button>
                    ` : alert.status === 'Contacted' ? `
                        <button class="btn-success btn-sm" onclick="alertsManager.markAsResolved('${alert.id}')">
                            ✅ Mark Resolved
                        </button>
                        <button class="btn-secondary btn-sm" onclick="alertsManager.viewStudent('${alert.student_id}')">
                            👁️ View Details
                        </button>
                    ` : `
                        <button class="btn-secondary btn-sm" onclick="alertsManager.viewStudent('${alert.student_id}')">
                            👁️ View Details
                        </button>
                        <span class="resolved-text">✅ Resolved</span>
                    `}
                </div>
            </div>
        `).join('');
    }

    contactStudent(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (!alert) return;

        this.currentStudent = alert;
        
        document.getElementById('contact-student-info').innerHTML = `
            <div class="student-contact-info">
                <h4>${alert.student_name} (${alert.student_id})</h4>
                <p><strong>Department:</strong> ${alert.department}</p>
                <p><strong>Risk Level:</strong> <span class="risk-badge ${alert.priority.toLowerCase()}">${alert.priority}</span></p>
                <p><strong>Email:</strong> ${alert.contact_info.email}</p>
                <p><strong>Phone:</strong> ${alert.contact_info.phone}</p>
                <p><strong>Mentor:</strong> ${alert.contact_info.mentor}</p>
                
                <div class="risk-summary">
                    <h5>Risk Factors:</h5>
                    <ul>
                        ${alert.risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;

        document.getElementById('contact-modal').style.display = 'block';
    }

    sendEmail() {
        if (!this.currentStudent) return;
        
        // Mock email sending
        Utils.showSuccess(`📧 Email sent to ${this.currentStudent.contact_info.email}`);
        this.addToHistory('Email', `Sent email to ${this.currentStudent.student_name}`);
    }

    sendSMS() {
        if (!this.currentStudent) return;
        
        // Mock SMS sending
        Utils.showSuccess(`📱 SMS sent to ${this.currentStudent.contact_info.phone}`);
        this.addToHistory('SMS', `Sent SMS to ${this.currentStudent.student_name}`);
    }

    contactMentor() {
        if (!this.currentStudent) return;
        
        // Mock mentor notification
        Utils.showSuccess(`👨🏫 Mentor notified: ${this.currentStudent.contact_info.mentor}`);
        this.addToHistory('Mentor Contact', `Notified mentor for ${this.currentStudent.student_name}`);
    }

    escalateToAdmin() {
        if (!this.currentStudent) return;
        
        // Mock admin escalation
        Utils.showSuccess(`⚠️ Alert escalated to college administration`);
        this.addToHistory('Escalation', `Escalated ${this.currentStudent.student_name} to admin`);
    }

    markAsContacted() {
        if (!this.currentStudent) return;
        
        const notes = document.getElementById('action-notes').value;
        
        // Update alert status in both arrays
        const alert = this.alerts.find(a => a.id === this.currentStudent.id);
        if (alert) {
            alert.status = 'Contacted';
            alert.notes = notes;
        }
        
        // Update filtered alerts as well
        this.filteredAlerts = this.filteredAlerts.map(a => 
            a.id === this.currentStudent.id ? {...a, status: 'Contacted', notes: notes} : a
        );
        
        this.addToHistory('Contacted', `Marked ${this.currentStudent.student_name} as contacted: ${notes}`);
        
        Utils.showSuccess('✅ Student marked as contacted');
        this.closeContactModal();
        this.renderAlerts();
        this.updateStatistics();
        
        // Force counter update
        setTimeout(() => {
            this.updateStatistics();
        }, 100);
    }

    markAsResolved(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (alert) {
            const oldStatus = alert.status;
            alert.status = 'Resolved';
            this.addToHistory('Resolved', `Resolved alert for ${alert.student_name}`);
            Utils.showSuccess('✅ Alert marked as resolved');
            
            // Update the filtered alerts as well
            this.filteredAlerts = this.filteredAlerts.map(a => 
                a.id === alertId ? {...a, status: 'Resolved'} : a
            );
            
            this.renderAlerts();
            this.updateStatistics();
            
            // Force re-render to sync counters
            setTimeout(() => {
                this.updateStatistics();
            }, 100);
        }
    }

    addToHistory(action, description) {
        this.alertHistory.unshift({
            timestamp: new Date().toISOString(),
            action: action,
            description: description,
            user: 'Current User'
        });
        
        this.updateAlertHistory();
    }

    updateAlertHistory() {
        const historyContainer = document.getElementById('alert-history');
        
        historyContainer.innerHTML = this.alertHistory.slice(0, 10).map(item => `
            <div class="history-item">
                <div class="history-content">
                    <strong>${item.action}</strong>: ${item.description}
                </div>
                <div class="history-meta">
                    <small>${new Date(item.timestamp).toLocaleString()} • ${item.user}</small>
                </div>
            </div>
        `).join('');
    }

    updateStatistics() {
        const criticalCount = this.alerts.filter(a => a.priority === 'Critical').length;
        const highCount = this.alerts.filter(a => a.priority === 'High').length;
        const contactedCount = this.alerts.filter(a => a.status === 'Contacted').length;
        const resolvedCount = this.alerts.filter(a => a.status === 'Resolved').length;

        document.getElementById('critical-alerts-count').textContent = criticalCount;
        document.getElementById('high-alerts-count').textContent = highCount;
        document.getElementById('contacted-count').textContent = contactedCount;
        document.getElementById('resolved-count').textContent = resolvedCount;
    }

    loadDepartments() {
        const departments = [...new Set(this.alerts.map(a => a.department))].filter(Boolean);
        const select = document.getElementById('alert-department-filter');
        
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept;
            option.textContent = dept;
            select.appendChild(option);
        });
    }

    async viewStudent(studentId) {
        try {
            const student = this.alerts.find(a => a.student_id === studentId)?.student_data;
            if (!student) {
                Utils.showError('Student not found');
                return;
            }
            
            this.showStudentModal(student);
        } catch (error) {
            console.error('Error viewing student:', error);
            Utils.showError('Failed to load student details');
        }
    }
    
    showStudentModal(student) {
        // Create modal if it doesn't exist
        let modal = document.getElementById('student-detail-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'student-detail-modal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 id="detail-student-name">Student Details</h3>
                        <button class="modal-close" onclick="closeStudentModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div id="student-details-content"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        document.getElementById('detail-student-name').textContent = student.name;
        document.getElementById('student-details-content').innerHTML = `
            <div class="student-detail-grid">
                <div class="detail-section">
                    <h4>📋 Basic Information</h4>
                    <p><strong>Student ID:</strong> ${student.student_id}</p>
                    <p><strong>Name:</strong> ${student.name}</p>
                    <p><strong>Department:</strong> ${student.department}</p>
                    <p><strong>Gender:</strong> ${student.gender || 'N/A'}</p>
                </div>
                <div class="detail-section">
                    <h4>📊 Academic Performance</h4>
                    <p><strong>Attendance:</strong> ${student.attendance_percentage}%</p>
                    <p><strong>Marks:</strong> ${student.marks}</p>
                    <p><strong>Risk Level:</strong> 
                        <span class="${Utils.getRiskBadgeClass(student.risk_level)}">${student.risk_level}</span>
                    </p>
                </div>
                <div class="detail-section">
                    <h4>🏠 Family Information</h4>
                    <p><strong>Family Income:</strong> ${Utils.formatCurrency(student.family_income)}</p>
                    <p><strong>Family Size:</strong> ${student.family_size}</p>
                    <p><strong>Region:</strong> ${student.region}</p>
                    <p><strong>Electricity:</strong> ${student.electricity}</p>
                    <p><strong>Internet Access:</strong> ${student.internet_access}</p>
                </div>
                <div class="detail-section">
                    <h4>🎓 Additional Details</h4>
                    <p><strong>Caste Category:</strong> ${student.caste_category}</p>
                    <p><strong>Family Education:</strong> ${student.family_education_background}</p>
                    <p><strong>City/Village:</strong> ${student.city_village_name}</p>
                    <p><strong>PUC/College:</strong> ${student.puc_college}</p>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    closeContactModal() {
        document.getElementById('contact-modal').style.display = 'none';
        document.getElementById('action-notes').value = '';
        this.currentStudent = null;
    }

    clearAlertFilters() {
        document.getElementById('alert-priority-filter').value = '';
        document.getElementById('alert-status-filter').value = '';
        document.getElementById('alert-department-filter').value = '';
        this.applyFilters();
    }

    async generateAlerts() {
        Utils.showSuccess('🔄 Generating new alerts from latest data...');
        await this.loadAlerts();
    }

    async refreshAlerts() {
        await this.loadAlerts();
        Utils.showSuccess('🔄 Alerts refreshed');
    }
}

// Global functions
window.refreshAlerts = () => alertsManager.refreshAlerts();
window.generateAlerts = () => alertsManager.generateAlerts();
window.clearAlertFilters = () => alertsManager.clearAlertFilters();
window.closeContactModal = () => alertsManager.closeContactModal();
window.sendEmail = () => alertsManager.sendEmail();
window.sendSMS = () => alertsManager.sendSMS();
window.contactMentor = () => alertsManager.contactMentor();
window.escalateToAdmin = () => alertsManager.escalateToAdmin();
window.markAsContacted = () => alertsManager.markAsContacted();
window.closeStudentModal = () => {
    const modal = document.getElementById('student-detail-modal');
    if (modal) modal.style.display = 'none';
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.alertsManager = new AlertsManager();
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});