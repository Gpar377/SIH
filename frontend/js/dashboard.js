// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.currentPage = 1;
        this.studentsPerPage = 10;
        this.currentFilters = {};
        this.students = [];
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadDashboardData();
        this.setupAutoRefresh();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(e.target.getAttribute('href'));
            });
        });

        // Filters
        const departmentFilter = document.getElementById('department-filter');
        const riskFilter = document.getElementById('risk-filter');
        
        if (departmentFilter) {
            departmentFilter.addEventListener('change', () => this.applyFilters());
        }
        
        if (riskFilter) {
            riskFilter.addEventListener('change', () => this.applyFilters());
        }

        // Pagination
        document.getElementById('prev-page')?.addEventListener('click', () => this.previousPage());
        document.getElementById('next-page')?.addEventListener('click', () => this.nextPage());

        // Refresh button
        document.querySelector('[onclick="refreshDashboard()"]')?.addEventListener('click', () => this.loadDashboardData());
        
        // Chart type selector
        const chartSelector = document.getElementById('chart-type-selector');
        if (chartSelector) {
            chartSelector.addEventListener('change', () => {
                this.loadDashboardData();
            });
        }
    }

    async loadDashboardData() {
        try {
            Utils.showLoading();
            
            // Force set GPJ session for testing
            sessionStorage.setItem('userCollege', 'gpj');
            sessionStorage.setItem('userRole', 'college');
            sessionStorage.setItem('isAuthenticated', 'true');
            console.log('Forced GPJ session set');
            
            // Get current user's college for filtering
            const userCollege = sessionStorage.getItem('userCollege');
            console.log('Loading dashboard for:', userCollege);
            
            // Load dashboard stats with college filter
            const stats = await API.getDashboardStats(userCollege);
            this.updateStatsCards(stats);
            
            // Get current user's college for filtering
            const userCollege = sessionStorage.getItem('userCollege');
            
            // Load alerts
            const alerts = await API.getAlerts(userCollege);
            this.updateAlertsPanel(alerts);
            
            // Load students
            await this.loadStudents();
            
            // Load departments for filter
            await this.loadDepartments();
            
            // Update risk chart
            this.updateRiskChart(stats.risk_distribution);
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
            Utils.showError('Failed to load dashboard data. Please refresh the page.');
        } finally {
            Utils.hideLoading();
        }
    }

    updateStatsCards(stats) {
        const { overview } = stats;
        
        document.getElementById('total-students').textContent = Utils.formatNumber(overview.total_students);
        document.getElementById('high-risk-students').textContent = Utils.formatNumber(overview.high_risk_students);
        document.getElementById('low-risk-students').textContent = Utils.formatNumber(overview.low_risk_students);
        document.getElementById('risk-percentage').textContent = `${overview.risk_percentage}%`;
    }

    updateAlertsPanel(alerts) {
        const alertsList = document.getElementById('alerts-list');
        const alertsCount = document.getElementById('alerts-count');
        
        if (!alertsList) return;
        
        alertsCount.textContent = alerts.total_alerts;
        
        if (alerts.alerts.length === 0) {
            alertsList.innerHTML = '<p class="no-alerts">No critical alerts at this time.</p>';
            return;
        }

        alertsList.innerHTML = alerts.alerts.slice(0, 5).map(alert => `
            <div class="alert-item ${alert.priority.toLowerCase()}">
                <div class="alert-avatar">
                    ${Utils.getInitials(alert.name)}
                </div>
                <div class="alert-content">
                    <h4>${alert.name}</h4>
                    <p>${alert.department} • ${alert.message}</p>
                </div>
                <button class="btn-secondary btn-sm" onclick="dashboard.viewStudent('${alert.student_id}')">
                    View
                </button>
            </div>
        `).join('');
    }

    async loadStudents() {
        try {
            // Get current user's college for filtering
            const userCollege = sessionStorage.getItem('userCollege');
            
            const params = {
                limit: this.studentsPerPage,
                offset: (this.currentPage - 1) * this.studentsPerPage,
                ...this.currentFilters
            };
            
            if (userCollege && userCollege !== 'government') {
                params.college_filter = userCollege;
            }
            
            const response = await API.getStudents(params);
            this.students = response.students;
            this.updateStudentsTable();
            this.updatePagination(response.total);
            
        } catch (error) {
            console.error('Error loading students:', error);
            Utils.showError('Failed to load students data.');
        }
    }

    updateStudentsTable() {
        const tbody = document.getElementById('students-table-body');
        if (!tbody) return;

        if (this.students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No students found</td></tr>';
            return;
        }

        tbody.innerHTML = this.students.map(student => `
            <tr>
                <td>
                    <div class="student-info">
                        <div class="student-avatar">
                            ${Utils.getInitials(student.name)}
                        </div>
                        <div>
                            <strong>${student.name}</strong>
                            <br>
                            <small>${student.student_id}</small>
                        </div>
                    </div>
                </td>
                <td>${student.department || 'N/A'}</td>
                <td>
                    <span class="attendance-value ${this.getAttendanceClass(student.attendance_percentage)}">
                        ${student.attendance_percentage || 0}%
                    </span>
                </td>
                <td>
                    <span class="marks-value ${this.getMarksClass(student.theory_marks)}">
                        ${student.theory_marks || 0}%
                    </span>
                </td>
                <td>
                    <span class="${Utils.getRiskBadgeClass(student.risk_level || 'Low')}">
                        ${student.risk_level || 'Low'}
                    </span>
                </td>
                <td>
                    <button class="btn-secondary btn-sm" onclick="dashboard.viewStudent('${student.student_id}')">
                        View
                    </button>
                    <button class="btn-secondary btn-sm" onclick="dashboard.editStudent('${student.student_id}')">
                        Edit
                    </button>
                </td>
            </tr>
        `).join('');
    }

    getAttendanceClass(attendance) {
        if (attendance < 45) return 'critical';
        if (attendance < 60) return 'high';
        if (attendance < 75) return 'medium';
        return 'good';
    }

    getMarksClass(marks) {
        if (marks < 40) return 'critical';
        if (marks < 55) return 'high';
        if (marks < 70) return 'medium';
        return 'good';
    }

    async loadDepartments() {
        try {
            const response = await API.getDepartments();
            const select = document.getElementById('department-filter');
            
            if (select && response.departments) {
                const currentValue = select.value;
                select.innerHTML = '<option value="">All Departments</option>';
                
                response.departments.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept;
                    option.textContent = dept;
                    select.appendChild(option);
                });
                
                select.value = currentValue;
            }
        } catch (error) {
            console.error('Error loading departments:', error);
        }
    }

    updateRiskChart(riskDistribution) {
        const canvas = document.getElementById('risk-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = [
            { label: 'Low Risk', value: riskDistribution.Low || 0, color: '#10b981', gradient: ['#10b981', '#059669'] },
            { label: 'Medium Risk', value: riskDistribution.Medium || 0, color: '#f59e0b', gradient: ['#f59e0b', '#d97706'] },
            { label: 'High Risk', value: riskDistribution.High || 0, color: '#ef4444', gradient: ['#ef4444', '#dc2626'] },
            { label: 'Critical Risk', value: riskDistribution.Critical || 0, color: '#991b1b', gradient: ['#991b1b', '#7f1d1d'] }
        ];

        const chartType = document.getElementById('chart-type-selector')?.value || 'doughnut';
        
        switch(chartType) {
            case 'doughnut':
                this.drawDoughnutChart(ctx, data, canvas.width, canvas.height);
                break;
            case 'bar':
                this.drawBarChart(ctx, data, canvas.width, canvas.height);
                break;
            case 'line':
                this.drawTrendChart(ctx, data, canvas.width, canvas.height);
                break;
        }
        
        this.updateChartLegend(data);
        this.drawDepartmentChart(riskDistribution);
        this.drawScatterChart();
    }

    drawDoughnutChart(ctx, data, width, height) {
        const centerX = width / 2;
        const centerY = height / 2;
        const outerRadius = Math.min(width, height) / 2 - 40;
        const innerRadius = outerRadius * 0.6;
        
        const total = data.reduce((sum, item) => sum + item.value, 0);
        
        if (total === 0) {
            this.drawNoDataMessage(ctx, centerX, centerY, outerRadius);
            return;
        }

        let currentAngle = -Math.PI / 2;
        
        // Draw segments with gradients and animations
        data.forEach((item, index) => {
            const sliceAngle = (item.value / total) * 2 * Math.PI;
            
            // Create gradient
            const gradient = ctx.createRadialGradient(centerX, centerY, innerRadius, centerX, centerY, outerRadius);
            gradient.addColorStop(0, item.gradient[0]);
            gradient.addColorStop(1, item.gradient[1]);
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(centerX, centerY, outerRadius, currentAngle, currentAngle + sliceAngle);
            ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
            ctx.closePath();
            ctx.fill();
            
            // Add subtle shadow
            ctx.shadowColor = 'rgba(0,0,0,0.1)';
            ctx.shadowBlur = 3;
            ctx.shadowOffsetX = 2;
            ctx.shadowOffsetY = 2;
            
            // Draw percentage labels
            if (sliceAngle > 0.1) {
                const percentage = Math.round((item.value / total) * 100);
                const labelAngle = currentAngle + sliceAngle / 2;
                const labelRadius = (outerRadius + innerRadius) / 2;
                const labelX = centerX + Math.cos(labelAngle) * labelRadius;
                const labelY = centerY + Math.sin(labelAngle) * labelRadius;
                
                ctx.shadowColor = 'transparent';
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 14px Inter';
                ctx.textAlign = 'center';
                ctx.fillText(`${percentage}%`, labelX, labelY);
            }
            
            currentAngle += sliceAngle;
        });
        
        // Reset shadow
        ctx.shadowColor = 'transparent';
        
        // Draw center text
        ctx.fillStyle = '#1f2937';
        ctx.font = 'bold 24px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(total.toString(), centerX, centerY - 5);
        
        ctx.fillStyle = '#6b7280';
        ctx.font = '14px Inter';
        ctx.fillText('Total Students', centerX, centerY + 15);
    }
    
    drawBarChart(ctx, data, width, height) {
        const padding = 60;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        const barWidth = chartWidth / data.length * 0.7;
        const maxValue = Math.max(...data.map(d => d.value));
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid lines
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }
        
        // Draw bars
        data.forEach((item, index) => {
            const barHeight = (item.value / maxValue) * chartHeight;
            const x = padding + (chartWidth / data.length) * index + (chartWidth / data.length - barWidth) / 2;
            const y = height - padding - barHeight;
            
            // Create gradient
            const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
            gradient.addColorStop(0, item.gradient[0]);
            gradient.addColorStop(1, item.gradient[1]);
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw value on top
            ctx.fillStyle = '#1f2937';
            ctx.font = 'bold 12px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(item.value.toString(), x + barWidth / 2, y - 5);
            
            // Draw label
            ctx.fillStyle = '#6b7280';
            ctx.font = '11px Inter';
            ctx.save();
            ctx.translate(x + barWidth / 2, height - padding + 15);
            ctx.rotate(-Math.PI / 4);
            ctx.fillText(item.label, 0, 0);
            ctx.restore();
        });
    }
    
    drawTrendChart(ctx, data, width, height) {
        const padding = 60;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        // Generate trend data (simulated)
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const trendData = data.map(item => ({
            ...item,
            trend: months.map(() => Math.max(0, item.value + Math.random() * 20 - 10))
        }));
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        const maxValue = Math.max(...trendData.flatMap(d => d.trend));
        
        // Draw grid
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }
        
        // Draw trend lines
        trendData.forEach((item, index) => {
            ctx.strokeStyle = item.color;
            ctx.lineWidth = 3;
            ctx.beginPath();
            
            item.trend.forEach((value, monthIndex) => {
                const x = padding + (chartWidth / (months.length - 1)) * monthIndex;
                const y = height - padding - (value / maxValue) * chartHeight;
                
                if (monthIndex === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Draw points
            ctx.fillStyle = item.color;
            item.trend.forEach((value, monthIndex) => {
                const x = padding + (chartWidth / (months.length - 1)) * monthIndex;
                const y = height - padding - (value / maxValue) * chartHeight;
                
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, 2 * Math.PI);
                ctx.fill();
            });
        });
        
        // Draw month labels
        ctx.fillStyle = '#6b7280';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        months.forEach((month, index) => {
            const x = padding + (chartWidth / (months.length - 1)) * index;
            ctx.fillText(month, x, height - padding + 20);
        });
    }
    
    drawDepartmentChart(riskDistribution) {
        const canvas = document.getElementById('department-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Show no data message when no students exist
        const departmentStats = [];
        
        if (departmentStats.length > 0) {
            this.drawHorizontalBarChart(ctx, departmentStats, canvas.width, canvas.height);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#64748b';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('No department data available', canvas.width / 2, canvas.height / 2);
        }
    }
    
    async calculateDepartmentStats() {
        try {
            // Get fresh student data for charts
            const response = await API.getStudents({ limit: 1000 });
            const students = response.students || response || [];
            
            const deptStats = {};
            
            students.forEach(student => {
                const dept = student.department || 'Unknown';
                if (!deptStats[dept]) {
                    deptStats[dept] = { total: 0, highRisk: 0 };
                }
                deptStats[dept].total++;
                if (['High', 'Critical'].includes(student.risk_level)) {
                    deptStats[dept].highRisk++;
                }
            });
            
            // Convert to array format for chart
            return Object.entries(deptStats).map(([name, stats]) => ({
                name: name,
                students: stats.total,
                highRisk: stats.highRisk
            })).sort((a, b) => b.students - a.students);
        } catch (error) {
            console.error('Error calculating department stats:', error);
            return [];
        }
    }
    
    drawScatterChart() {
        const canvas = document.getElementById('scatter-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Show no data message
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#64748b';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No attendance/performance data available', canvas.width / 2, canvas.height / 2);
    }
    
    drawHorizontalBarChart(ctx, data, width, height) {
        const padding = 80;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        const barHeight = chartHeight / data.length * 0.7;
        const maxValue = Math.max(...data.map(d => d.students));
        
        ctx.clearRect(0, 0, width, height);
        
        data.forEach((item, index) => {
            const barWidth = (item.students / maxValue) * chartWidth;
            const y = padding + (chartHeight / data.length) * index + (chartHeight / data.length - barHeight) / 2;
            
            // Draw background bar
            ctx.fillStyle = '#e5e7eb';
            ctx.fillRect(padding, y, chartWidth, barHeight);
            
            // Draw data bar
            const gradient = ctx.createLinearGradient(padding, 0, padding + barWidth, 0);
            gradient.addColorStop(0, '#3b82f6');
            gradient.addColorStop(1, '#1d4ed8');
            ctx.fillStyle = gradient;
            ctx.fillRect(padding, y, barWidth, barHeight);
            
            // Draw high risk overlay
            const riskWidth = (item.highRisk / maxValue) * chartWidth;
            ctx.fillStyle = '#ef4444';
            ctx.fillRect(padding, y, riskWidth, barHeight);
            
            // Draw department name
            ctx.fillStyle = '#1f2937';
            ctx.font = '12px Inter';
            ctx.textAlign = 'right';
            ctx.fillText(item.name, padding - 10, y + barHeight / 2 + 4);
            
            // Draw values
            ctx.textAlign = 'left';
            ctx.fillText(`${item.students} (${item.highRisk} at risk)`, padding + barWidth + 10, y + barHeight / 2 + 4);
        });
    }
    
    drawScatterPlot(ctx, data, width, height) {
        const padding = 60;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 10; i++) {
            const x = padding + (chartWidth / 10) * i;
            const y = padding + (chartHeight / 10) * i;
            
            ctx.beginPath();
            ctx.moveTo(x, padding);
            ctx.lineTo(x, height - padding);
            ctx.stroke();
            
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }
        
        // Draw points
        data.forEach(point => {
            const x = padding + (point.attendance / 100) * chartWidth;
            const y = height - padding - (point.marks / 100) * chartHeight;
            
            const colors = {
                low: '#10b981',
                medium: '#f59e0b',
                high: '#ef4444'
            };
            
            ctx.fillStyle = colors[point.risk];
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, 2 * Math.PI);
            ctx.fill();
        });
        
        // Draw axes labels
        ctx.fillStyle = '#6b7280';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText('Attendance %', width / 2, height - 20);
        
        ctx.save();
        ctx.translate(20, height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText('Marks %', 0, 0);
        ctx.restore();
    }
    
    updateChartLegend(data) {
        const legend = document.getElementById('chart-legend');
        if (!legend) return;
        
        legend.innerHTML = data.map(item => `
            <div class="legend-item">
                <div class="legend-color" style="background: ${item.color}"></div>
                <span class="legend-label">${item.label}: ${item.value}</span>
            </div>
        `).join('');
    }
    
    drawNoDataMessage(ctx, centerX, centerY, radius) {
        ctx.fillStyle = '#e2e8f0';
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.fillStyle = '#64748b';
        ctx.font = '16px Inter';
        ctx.textAlign = 'center';
        ctx.fillText('No Data Available', centerX, centerY);
    }

    applyFilters() {
        const departmentFilter = document.getElementById('department-filter');
        const riskFilter = document.getElementById('risk-filter');
        
        this.currentFilters = {};
        
        if (departmentFilter?.value) {
            this.currentFilters.department = departmentFilter.value;
        }
        
        if (riskFilter?.value) {
            this.currentFilters.risk_level = riskFilter.value;
        }
        
        this.currentPage = 1;
        this.loadStudents();
    }

    updatePagination(total) {
        const totalPages = Math.ceil(total / this.studentsPerPage);
        const pageInfo = document.getElementById('page-info');
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        if (pageInfo) {
            pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        }
        
        if (prevBtn) {
            prevBtn.disabled = this.currentPage <= 1;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= totalPages;
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadStudents();
        }
    }

    nextPage() {
        this.currentPage++;
        this.loadStudents();
    }

    async viewStudent(studentId) {
        try {
            Utils.showLoading();
            const response = await API.getStudent(studentId);
            this.showStudentModal(response.student, response.risk_breakdown);
        } catch (error) {
            console.error('Error loading student:', error);
            Utils.showError('Failed to load student details.');
        } finally {
            Utils.hideLoading();
        }
    }

    showStudentModal(student, riskBreakdown) {
        const modal = document.getElementById('student-modal');
        const modalName = document.getElementById('modal-student-name');
        const modalBody = document.getElementById('student-details');
        
        if (!modal) return;
        
        modalName.textContent = student.name;
        
        modalBody.innerHTML = `
            <div class="student-detail-grid">
                <div class="student-basic-info">
                    <h4>Basic Information</h4>
                    <p><strong>Student ID:</strong> ${student.student_id}</p>
                    <p><strong>Department:</strong> ${student.department}</p>
                    <p><strong>Semester:</strong> ${student.semester}</p>
                    <p><strong>Region:</strong> ${student.region}</p>
                </div>
                
                <div class="risk-breakdown">
                    <h4>Risk Analysis</h4>
                    <div class="risk-score">
                        <span class="score-value">${riskBreakdown.composite_score}/100</span>
                        <span class="${Utils.getRiskBadgeClass(riskBreakdown.risk_level)}">${riskBreakdown.risk_level}</span>
                    </div>
                    
                    <div class="risk-components">
                        ${Object.entries(riskBreakdown.components).map(([key, component]) => `
                            <div class="component">
                                <strong>${key.charAt(0).toUpperCase() + key.slice(1)}:</strong>
                                <span class="${Utils.getRiskBadgeClass(component.level)}">${component.level}</span>
                                <p>${component.message}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="recommendations">
                    <h4>Recommendations</h4>
                    <ul>
                        ${riskBreakdown.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        modal.classList.add('active');
        
        // Close modal handlers
        modal.querySelector('.modal-close').onclick = () => modal.classList.remove('active');
        modal.onclick = (e) => {
            if (e.target === modal) modal.classList.remove('active');
        };
    }

    async editStudent(studentId) {
        // This would open an edit form - simplified for now
        const newAttendance = prompt('Enter new attendance percentage:');
        if (newAttendance && !isNaN(newAttendance)) {
            try {
                Utils.showLoading();
                await API.updateStudent(studentId, {
                    attendance_percentage: parseFloat(newAttendance)
                });
                Utils.showSuccess('Student updated successfully!');
                this.loadStudents();
            } catch (error) {
                Utils.showError('Failed to update student.');
            } finally {
                Utils.hideLoading();
            }
        }
    }

    handleNavigation(href) {
        // Simple navigation - in a real app you'd use a router
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        document.querySelector(`[href="${href}"]`)?.classList.add('active');
        
        if (href === '/upload') {
            window.location.href = '/upload';
        }
    }

    setupAutoRefresh() {
        // Refresh dashboard every 5 minutes
        setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Students Management Functions
let studentsData = [];
let filteredStudentsData = [];
let currentStudentsPage = 1;
const studentsPerPage = 20;

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Load section-specific data
    if (sectionName === 'students') {
        loadAllStudents();
    }
}

async function loadAllStudents() {
    try {
        Utils.showLoading();
        const response = await API.getStudents({ limit: 2000 });
        studentsData = response.students || response || [];
        filteredStudentsData = [...studentsData];
        
        loadStudentsDepartments();
        renderAllStudents();
        updateStudentsCount();
    } catch (error) {
        console.error('Error loading students:', error);
        Utils.showError('Failed to load students');
    } finally {
        Utils.hideLoading();
    }
}

function loadStudentsDepartments() {
    const departments = [...new Set(studentsData.map(s => s.department))].filter(Boolean);
    const select = document.getElementById('students-department-filter');
    select.innerHTML = '<option value="">All Departments</option>';
    
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept;
        option.textContent = dept;
        select.appendChild(option);
    });
}

function searchStudents() {
    applyStudentFilters();
}

function applyStudentFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const deptFilter = document.getElementById('students-department-filter').value;
    const riskFilter = document.getElementById('students-risk-filter').value;
    const regionFilter = document.getElementById('students-region-filter').value;
    
    filteredStudentsData = studentsData.filter(student => {
        const matchesSearch = !searchTerm || 
            student.name?.toLowerCase().includes(searchTerm) ||
            student.student_id?.toLowerCase().includes(searchTerm);
        
        const matchesDept = !deptFilter || student.department === deptFilter;
        const matchesRisk = !riskFilter || student.risk_level === riskFilter;
        const matchesRegion = !regionFilter || student.region === regionFilter;
        
        return matchesSearch && matchesDept && matchesRisk && matchesRegion;
    });
    
    currentStudentsPage = 1;
    renderAllStudents();
    updateStudentsCount();
}

function renderAllStudents() {
    const tbody = document.getElementById('all-students-table-body');
    const startIndex = (currentStudentsPage - 1) * studentsPerPage;
    const endIndex = startIndex + studentsPerPage;
    const studentsToShow = filteredStudentsData.slice(startIndex, endIndex);
    
    tbody.innerHTML = studentsToShow.map(student => `
        <tr>
            <td>${student.student_id || 'N/A'}</td>
            <td>${student.name || 'N/A'}</td>
            <td>${student.department || 'N/A'}</td>
            <td>
                <span class="attendance-badge ${getAttendanceBadgeClass(student.attendance_percentage)}">
                    ${student.attendance_percentage || 0}%
                </span>
            </td>
            <td>${student.marks || 0}</td>
            <td>${Utils.formatCurrency(student.family_income || 0)}</td>
            <td>${student.region || 'N/A'}</td>
            <td>
                <span class="${Utils.getRiskBadgeClass(student.risk_level || 'Low')}">
                    ${student.risk_level || 'Low'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn-sm btn-primary" onclick="viewStudentDetails('${student.student_id}')">
                        👁️ View
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    updateStudentsPagination();
}

function getAttendanceBadgeClass(attendance) {
    if (attendance >= 75) return 'success';
    if (attendance >= 60) return 'warning';
    return 'danger';
}

function updateStudentsPagination() {
    const totalPages = Math.ceil(filteredStudentsData.length / studentsPerPage);
    document.getElementById('students-page-info').textContent = `Page ${currentStudentsPage} of ${totalPages}`;
    
    document.getElementById('students-prev-page').disabled = currentStudentsPage === 1;
    document.getElementById('students-next-page').disabled = currentStudentsPage === totalPages;
}

function updateStudentsCount() {
    document.getElementById('students-count-display').textContent = 
        `${filteredStudentsData.length} students found`;
}

function changeStudentsPage(direction) {
    const totalPages = Math.ceil(filteredStudentsData.length / studentsPerPage);
    const newPage = currentStudentsPage + direction;
    
    if (newPage >= 1 && newPage <= totalPages) {
        currentStudentsPage = newPage;
        renderAllStudents();
    }
}

function clearStudentFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('students-department-filter').value = '';
    document.getElementById('students-risk-filter').value = '';
    document.getElementById('students-region-filter').value = '';
    applyStudentFilters();
}

function viewStudentDetails(studentId) {
    const student = studentsData.find(s => s.student_id === studentId);
    if (!student) return;
    
    document.getElementById('modal-student-name').textContent = student.name;
    document.getElementById('student-details').innerHTML = `
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
        </div>
    `;
    
    document.getElementById('student-modal').style.display = 'block';
}

function exportStudents() {
    try {
        const csvContent = generateStudentsCSV(filteredStudentsData);
        Utils.downloadFile(csvContent, 'students_export.csv', 'text/csv');
        Utils.showSuccess('Students exported successfully!');
    } catch (error) {
        console.error('Error exporting students:', error);
        Utils.showError('Failed to export students');
    }
}

function generateStudentsCSV(students) {
    const headers = [
        'Student ID', 'Name', 'Department', 'Attendance %', 'Marks', 
        'Family Income', 'Region', 'Risk Level'
    ];
    
    const rows = students.map(student => [
        student.student_id,
        student.name,
        student.department,
        student.attendance_percentage,
        student.marks,
        student.family_income,
        student.region,
        student.risk_level
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
}

// Global functions for onclick handlers
window.refreshDashboard = () => {
    if (window.dashboard) {
        window.dashboard.loadDashboardData();
    }
};

window.exportStudents = () => {
    // Simple CSV export
    const csvContent = "data:text/csv;charset=utf-8," 
        + "Name,Department,Attendance,Marks,Risk Level\n"
        + window.dashboard.students.map(s => 
            `${s.name},${s.department},${s.attendance_percentage},${s.theory_marks},${s.risk_level}`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "students_export.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

// Authentication functions
function checkAuthentication() {
    const isAuthenticated = sessionStorage.getItem('isAuthenticated');
    const userRole = sessionStorage.getItem('userRole');
    const userCollege = sessionStorage.getItem('userCollege');
    const username = sessionStorage.getItem('username');
    
    if (!isAuthenticated || isAuthenticated !== 'true') {
        // For demo purposes, allow access but show login option
        console.log('Not authenticated, but allowing demo access');
        document.getElementById('user-display').textContent = 'Demo User';
        return true; // Allow demo access
    }
    
    // Update user display
    updateUserDisplay(userRole, userCollege, username);
    
    // Apply role-based restrictions
    applyRoleRestrictions(userRole, userCollege);
    
    return true;
}

function updateUserDisplay(role, college, username) {
    const userDisplay = document.getElementById('user-display');
    const loginBtn = document.querySelector('.btn-primary');
    const logoutBtn = document.getElementById('logout-btn');
    
    if (role === 'government') {
        userDisplay.textContent = 'Government Admin';
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
    } else if (role === 'college') {
        const collegeNames = {
            'gpj': 'GPJ Admin',
            'rtu': 'RTU Admin', 
            'geca': 'GEC Admin',
            'itij': 'ITI Admin',
            'polu': 'Poly Admin'
        };
        userDisplay.textContent = collegeNames[college] || 'College Admin';
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
    } else {
        userDisplay.textContent = 'Demo User';
        loginBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
    }
}

function applyRoleRestrictions(role, college) {
    const collegeSelector = document.getElementById('college-selector');
    
    if (role === 'government') {
        // Government users see college selector
        collegeSelector.style.display = 'inline-block';
        console.log('Government user - showing college selector');
        
    } else if (role === 'college') {
        // College users see only their data
        collegeSelector.style.display = 'none';
        console.log(`College user: ${college}`);
        
        // Update page title to show college
        const collegeNames = {
            'gpj': 'Government Polytechnic Jaipur',
            'rtu': 'Rajasthan Technical University Kota', 
            'geca': 'Government Engineering College Ajmer',
            'itij': 'Industrial Training Institute Jodhpur',
            'polu': 'Polytechnic College Udaipur'
        };
        
        const pageTitle = document.querySelector('h2');
        if (pageTitle) {
            pageTitle.textContent = `${collegeNames[college]} - Dashboard`;
        }
    } else {
        // Demo user - hide selector
        collegeSelector.style.display = 'none';
    }
}

function changeCollege() {
    const selector = document.getElementById('college-selector');
    const selectedCollege = selector.value;
    
    console.log(`Switching to college: ${selectedCollege}`);
    
    // Update page title
    const pageTitle = document.querySelector('h2');
    if (selectedCollege === 'all') {
        pageTitle.textContent = 'All Colleges - Dashboard';
    } else {
        const collegeNames = {
            'gpj': 'Government Polytechnic Jaipur',
            'rtu': 'Rajasthan Technical University Kota',
            'geca': 'Government Engineering College Ajmer', 
            'itij': 'Industrial Training Institute Jodhpur',
            'polu': 'Polytechnic College Udaipur'
        };
        pageTitle.textContent = `${collegeNames[selectedCollege]} - Dashboard`;
    }
    
    // Reload dashboard data for selected college
    if (window.dashboard) {
        window.dashboard.loadDashboardData();
    }
}

function logout() {
    // Clear session data
    sessionStorage.removeItem('isAuthenticated');
    sessionStorage.removeItem('userRole');
    sessionStorage.removeItem('userCollege');
    sessionStorage.removeItem('username');
    
    // Redirect to login
    window.location.href = '/login';
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication and initialize
    if (checkAuthentication()) {
        window.dashboard = new Dashboard();
    }
});