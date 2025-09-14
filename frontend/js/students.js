// Students Page JavaScript
class StudentsManager {
    constructor() {
        this.currentPage = 1;
        this.studentsPerPage = 20;
        this.allStudents = [];
        this.filteredStudents = [];
        this.selectedStudents = [];
        
        this.init();
    }

    async init() {
        await this.loadStudents();
        this.setupEventListeners();
        this.loadDepartments();
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', Utils.debounce(() => {
            this.applyFilters();
        }, 300));

        // Filter dropdowns
        ['department-filter', 'risk-filter', 'region-filter'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => {
                this.applyFilters();
            });
        });

        // Select all checkbox
        document.getElementById('select-all-checkbox').addEventListener('change', (e) => {
            this.toggleSelectAll(e.target.checked);
        });

        // Edit form submission
        document.getElementById('edit-student-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveStudentChanges();
        });
    }

    async loadStudents() {
        try {
            Utils.showLoading();
            const response = await API.getStudents();
            this.allStudents = response.students || response || [];
            this.filteredStudents = [...this.allStudents];
            this.renderStudents();
            this.updateStudentsCount();
        } catch (error) {
            console.error('Error loading students:', error);
            Utils.showError('Failed to load students: ' + error.message);
        } finally {
            Utils.hideLoading();
        }
    }

    async loadDepartments() {
        try {
            const departments = [...new Set(this.allStudents.map(s => s.department))];
            const departmentFilter = document.getElementById('department-filter');
            
            departments.forEach(dept => {
                if (dept) {
                    const option = document.createElement('option');
                    option.value = dept;
                    option.textContent = dept;
                    departmentFilter.appendChild(option);
                }
            });
        } catch (error) {
            console.error('Error loading departments:', error);
        }
    }

    applyFilters() {
        const searchTerm = document.getElementById('search-input').value.toLowerCase();
        const departmentFilter = document.getElementById('department-filter').value;
        const riskFilter = document.getElementById('risk-filter').value;
        const regionFilter = document.getElementById('region-filter').value;

        this.filteredStudents = this.allStudents.filter(student => {
            const matchesSearch = !searchTerm || 
                student.name?.toLowerCase().includes(searchTerm) ||
                student.student_id?.toLowerCase().includes(searchTerm);
            
            const matchesDepartment = !departmentFilter || student.department === departmentFilter;
            const matchesRisk = !riskFilter || student.risk_level === riskFilter;
            const matchesRegion = !regionFilter || student.region === regionFilter;

            return matchesSearch && matchesDepartment && matchesRisk && matchesRegion;
        });

        this.currentPage = 1;
        this.renderStudents();
        this.updateStudentsCount();
    }

    renderStudents() {
        const tbody = document.getElementById('students-table-body');
        const startIndex = (this.currentPage - 1) * this.studentsPerPage;
        const endIndex = startIndex + this.studentsPerPage;
        const studentsToShow = this.filteredStudents.slice(startIndex, endIndex);

        tbody.innerHTML = studentsToShow.map(student => `
            <tr>
                <td>
                    <input type="checkbox" class="student-checkbox" value="${student.student_id}">
                </td>
                <td>${student.student_id || 'N/A'}</td>
                <td>${student.name || 'N/A'}</td>
                <td>${student.department || 'N/A'}</td>
                <td>
                    <span class="attendance-badge ${this.getAttendanceBadgeClass(student.attendance_percentage)}">
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
                        <button class="btn-sm btn-primary" onclick="studentsManager.viewStudent('${student.student_id}')">
                            👁️ View
                        </button>
                        <button class="btn-sm btn-secondary" onclick="studentsManager.editStudent('${student.student_id}')">
                            ✏️ Edit
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        this.updatePagination();
    }

    getAttendanceBadgeClass(attendance) {
        if (attendance >= 75) return 'success';
        if (attendance >= 60) return 'warning';
        return 'danger';
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredStudents.length / this.studentsPerPage);
        document.getElementById('page-info').textContent = `Page ${this.currentPage} of ${totalPages}`;
        
        document.getElementById('prev-page').disabled = this.currentPage === 1;
        document.getElementById('next-page').disabled = this.currentPage === totalPages;
    }

    updateStudentsCount() {
        document.getElementById('students-count').textContent = 
            `${this.filteredStudents.length} students found`;
    }

    changePage(direction) {
        const totalPages = Math.ceil(this.filteredStudents.length / this.studentsPerPage);
        const newPage = this.currentPage + direction;
        
        if (newPage >= 1 && newPage <= totalPages) {
            this.currentPage = newPage;
            this.renderStudents();
        }
    }

    viewStudent(studentId) {
        const student = this.allStudents.find(s => s.student_id === studentId);
        if (!student) return;

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

        document.getElementById('student-detail-modal').style.display = 'block';
    }

    editStudent(studentId) {
        const student = this.allStudents.find(s => s.student_id === studentId);
        if (!student) return;

        // Populate edit form
        document.getElementById('edit-student-id').value = student.student_id;
        document.getElementById('edit-name').value = student.name || '';
        document.getElementById('edit-department').value = student.department || '';
        document.getElementById('edit-attendance').value = student.attendance_percentage || '';
        document.getElementById('edit-marks').value = student.marks || '';
        document.getElementById('edit-income').value = student.family_income || '';

        document.getElementById('edit-student-modal').style.display = 'block';
    }

    async saveStudentChanges() {
        try {
            const studentId = document.getElementById('edit-student-id').value;
            const updates = {
                name: document.getElementById('edit-name').value,
                department: document.getElementById('edit-department').value,
                attendance_percentage: parseFloat(document.getElementById('edit-attendance').value),
                marks: parseFloat(document.getElementById('edit-marks').value),
                family_income: parseFloat(document.getElementById('edit-income').value)
            };

            Utils.showLoading();
            await API.updateStudent(studentId, updates);
            
            // Update local data
            const studentIndex = this.allStudents.findIndex(s => s.student_id === studentId);
            if (studentIndex !== -1) {
                Object.assign(this.allStudents[studentIndex], updates);
            }

            this.applyFilters();
            this.closeEditModal();
            Utils.showSuccess('Student updated successfully!');

        } catch (error) {
            console.error('Error updating student:', error);
            Utils.showError('Failed to update student: ' + error.message);
        } finally {
            Utils.hideLoading();
        }
    }

    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.student-checkbox');
        checkboxes.forEach(cb => cb.checked = checked);
        this.updateSelectedStudents();
    }

    updateSelectedStudents() {
        const checkboxes = document.querySelectorAll('.student-checkbox:checked');
        this.selectedStudents = Array.from(checkboxes).map(cb => cb.value);
    }

    clearFilters() {
        document.getElementById('search-input').value = '';
        document.getElementById('department-filter').value = '';
        document.getElementById('risk-filter').value = '';
        document.getElementById('region-filter').value = '';
        this.applyFilters();
    }

    closeEditModal() {
        document.getElementById('edit-student-modal').style.display = 'none';
    }

    closeDetailModal() {
        document.getElementById('student-detail-modal').style.display = 'none';
    }

    async exportStudents() {
        try {
            const csvContent = this.generateCSV(this.filteredStudents);
            Utils.downloadFile(csvContent, 'students_export.csv', 'text/csv');
            Utils.showSuccess('Students exported successfully!');
        } catch (error) {
            console.error('Error exporting students:', error);
            Utils.showError('Failed to export students');
        }
    }

    generateCSV(students) {
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
}

// Global functions
window.searchStudents = () => studentsManager.applyFilters();
window.clearFilters = () => studentsManager.clearFilters();
window.selectAll = () => {
    const checkbox = document.getElementById('select-all-checkbox');
    studentsManager.toggleSelectAll(checkbox.checked);
};
window.bulkAction = () => {
    studentsManager.updateSelectedStudents();
    if (studentsManager.selectedStudents.length === 0) {
        Utils.showError('Please select students first');
        return;
    }
    Utils.showSuccess(`${studentsManager.selectedStudents.length} students selected`);
};
window.changePage = (direction) => studentsManager.changePage(direction);
window.exportStudents = () => studentsManager.exportStudents();
window.closeEditModal = () => studentsManager.closeEditModal();
window.closeDetailModal = () => studentsManager.closeDetailModal();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.studentsManager = new StudentsManager();
});

// Close modals when clicking outside
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});