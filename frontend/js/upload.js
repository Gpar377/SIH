// Upload Page JavaScript
class UploadManager {
    constructor() {
        this.currentStep = 1;
        this.uploadedFile = null;
        this.sessionId = null;
        this.columnMappings = {};
        this.fileData = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateProgressIndicator();
    }

    setupEventListeners() {
        // File input and drop zone
        const fileInput = document.getElementById('file-input');
        const dropZone = document.getElementById('drop-zone');

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // Drag and drop
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });

        dropZone.addEventListener('click', () => {
            fileInput.click();
        });
    }

    async handleFileSelect(file) {
        // Validate file type
        const allowedTypes = ['.csv', '.xlsx', '.xls'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExt)) {
            Utils.showError('Please select a CSV or Excel file.');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            Utils.showError('File size must be less than 10MB.');
            return;
        }

        this.uploadedFile = file;
        
        try {
            Utils.showLoading();
            
            // Upload file and get column information
            const response = await API.uploadFile(file);
            
            this.sessionId = response.session_id;
            this.fileData = response;
            
            // Show file info
            this.showFileInfo(response);
            
            // Generate column mapping interface
            this.generateColumnMapping(response.column_info);
            
            // Move to step 2
            this.goToStep(2);
            
        } catch (error) {
            console.error('Upload error:', error);
            Utils.showError('Failed to upload file: ' + error.message);
        } finally {
            Utils.hideLoading();
        }
    }

    showFileInfo(data) {
        const dropZone = document.getElementById('drop-zone');
        dropZone.innerHTML = `
            <div class="file-selected">
                <div class="file-icon">📄</div>
                <div class="file-details">
                    <h4>${data.filename}</h4>
                    <p>${Utils.formatNumber(data.total_rows)} rows detected</p>
                    <button class="btn-secondary btn-sm" onclick="uploadManager.selectNewFile()">
                        Change File
                    </button>
                </div>
            </div>
        `;
    }

    generateColumnMapping(columnInfo) {
        const mappingForm = document.getElementById('mapping-form');
        const previewTable = document.getElementById('file-preview-table');
        
        // Show file preview
        if (this.fileData.sample_data && this.fileData.sample_data.length > 0) {
            const headers = Object.keys(this.fileData.sample_data[0]);
            
            previewTable.innerHTML = `
                <table class="sample-table">
                    <thead>
                        <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${this.fileData.sample_data.slice(0, 3).map(row => 
                            `<tr>${headers.map(h => `<td>${row[h] || ''}</td>`).join('')}</tr>`
                        ).join('')}
                    </tbody>
                </table>
            `;
        }

        // Generate mapping form
        const systemFields = [
            { value: '', label: 'Select field...' },
            { value: 'student_id', label: 'Student ID', required: true },
            { value: 'name', label: 'Student Name', required: true },
            { value: 'attendance_percentage', label: 'Attendance %', required: true },
            { value: 'marks', label: 'Marks', required: true },
            { value: 'department', label: 'Department' },
            { value: 'semester', label: 'Semester' },
            { value: 'family_income', label: 'Family Income' },
            { value: 'family_size', label: 'Family Size' },
            { value: 'region', label: 'Region (Urban/Rural)' },
            { value: 'electricity', label: 'Electricity Access' },
            { value: 'internet_access', label: 'Internet Access' },
            { value: 'distance_from_college', label: 'Distance from College' },
            { value: 'age', label: 'Age' },
            { value: 'batch_year', label: 'Batch Year' }
        ];

        mappingForm.innerHTML = columnInfo.user_columns.map(userCol => {
            const suggestion = columnInfo.suggestions[userCol] || '';
            
            return `
                <div class="mapping-row">
                    <label>${userCol}</label>
                    <select class="mapping-select" data-user-column="${userCol}">
                        ${systemFields.map(field => 
                            `<option value="${field.value}" ${field.value === suggestion ? 'selected' : ''}>
                                ${field.label}${field.required ? ' *' : ''}
                            </option>`
                        ).join('')}
                    </select>
                </div>
            `;
        }).join('');

        // Add event listeners to mapping selects
        mappingForm.querySelectorAll('.mapping-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const userColumn = e.target.dataset.userColumn;
                const systemColumn = e.target.value;
                
                if (systemColumn) {
                    this.columnMappings[userColumn] = systemColumn;
                } else {
                    delete this.columnMappings[userColumn];
                }
                
                this.validateMappings();
            });
        });

        // Initialize mappings with suggestions
        Object.entries(columnInfo.suggestions).forEach(([userCol, systemCol]) => {
            this.columnMappings[userCol] = systemCol;
        });

        this.validateMappings();
    }

    validateMappings() {
        const requiredFields = ['student_id', 'name', 'attendance_percentage', 'marks'];
        const mappedFields = Object.values(this.columnMappings);
        const missingFields = requiredFields.filter(field => !mappedFields.includes(field));
        
        const processBtn = document.querySelector('[onclick="processData()"]');
        
        if (missingFields.length > 0) {
            processBtn.disabled = true;
            processBtn.textContent = `Missing: ${missingFields.join(', ')}`;
        } else {
            processBtn.disabled = false;
            processBtn.textContent = 'Process Data →';
        }
    }

    async processData() {
        if (!this.uploadedFile || !this.sessionId) {
            Utils.showError('Please upload a file first.');
            return;
        }

        try {
            this.goToStep(3);
            
            // Show processing status
            document.getElementById('processing-status').style.display = 'block';
            document.getElementById('results-summary').style.display = 'none';
            
            // Process data with mappings
            const response = await API.processData(this.columnMappings, this.sessionId, this.uploadedFile);
            
            if (response.success) {
                this.showResults(response.stats);
            } else {
                throw new Error(response.errors?.join(', ') || 'Processing failed');
            }
            
        } catch (error) {
            console.error('Processing error:', error);
            Utils.showError('Failed to process data: ' + error.message);
            this.goToStep(2); // Go back to mapping step
        }
    }

    showResults(stats) {
        document.getElementById('processing-status').style.display = 'none';
        document.getElementById('results-summary').style.display = 'block';
        
        // Update result statistics
        document.getElementById('processed-count').textContent = Utils.formatNumber(stats.total_students);
        document.getElementById('high-risk-count').textContent = Utils.formatNumber(stats.high_risk_students);
        
        // Show ML accuracy if available
        const mlAccuracy = stats.ml_training?.random_forest_accuracy;
        if (mlAccuracy) {
            document.getElementById('ml-accuracy').textContent = `${Math.round(mlAccuracy * 100)}%`;
        } else {
            document.getElementById('ml-accuracy').textContent = 'N/A';
        }
        
        // Show validation messages
        const validationDiv = document.getElementById('validation-messages');
        const validation = stats.validation;
        
        let messages = [];
        
        if (validation.errors && validation.errors.length > 0) {
            messages.push(...validation.errors.map(err => 
                `<div class="validation-message error">❌ ${err}</div>`
            ));
        }
        
        if (validation.warnings && validation.warnings.length > 0) {
            messages.push(...validation.warnings.map(warn => 
                `<div class="validation-message warning">⚠️ ${warn}</div>`
            ));
        }
        
        if (messages.length === 0) {
            messages.push('<div class="validation-message success">✅ All data processed successfully</div>');
        }
        
        validationDiv.innerHTML = messages.join('');
    }

    goToStep(step) {
        // Hide all steps
        document.querySelectorAll('.upload-step').forEach(stepEl => {
            stepEl.classList.remove('active');
        });
        
        // Show target step
        document.getElementById(`step-${step}`).classList.add('active');
        
        // Update progress indicator
        this.currentStep = step;
        this.updateProgressIndicator();
    }

    updateProgressIndicator() {
        document.querySelectorAll('.progress-step').forEach((step, index) => {
            const stepNumber = index + 1;
            if (stepNumber <= this.currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }

    selectNewFile() {
        // Reset state
        this.uploadedFile = null;
        this.sessionId = null;
        this.columnMappings = {};
        this.fileData = null;
        
        // Reset UI
        const dropZone = document.getElementById('drop-zone');
        dropZone.innerHTML = `
            <div class="drop-zone-content">
                <div class="upload-icon">📁</div>
                <h3>Drag & Drop your file here</h3>
                <p>or <button class="btn-link" onclick="document.getElementById('file-input').click()">browse files</button></p>
                <p class="file-info">Supports: .csv, .xlsx, .xls files</p>
            </div>
        `;
        
        this.goToStep(1);
    }

    goToDashboard() {
        window.location.href = '/';
    }

    uploadAnother() {
        this.selectNewFile();
    }

    async downloadSampleFormat() {
        try {
            const response = await API.getSampleFormat();
            
            // Create CSV content
            const headers = response.columns.join(',');
            const sampleRow = response.sample_rows[0];
            const values = response.columns.map(col => sampleRow[col] || '').join(',');
            
            const csvContent = `${headers}\n${values}`;
            
            Utils.downloadFile(csvContent, 'sample_format.csv', 'text/csv');
            
        } catch (error) {
            console.error('Error downloading sample:', error);
            Utils.showError('Failed to download sample format.');
        }
    }
}

// Global functions for onclick handlers
window.goToStep = (step) => {
    if (window.uploadManager) {
        window.uploadManager.goToStep(step);
    }
};

window.processData = () => {
    if (window.uploadManager) {
        window.uploadManager.processData();
    }
};

window.goToDashboard = () => {
    if (window.uploadManager) {
        window.uploadManager.goToDashboard();
    }
};

window.uploadAnother = () => {
    if (window.uploadManager) {
        window.uploadManager.uploadAnother();
    }
};

window.downloadSampleFormat = () => {
    if (window.uploadManager) {
        window.uploadManager.downloadSampleFormat();
    }
};

// Initialize upload manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.uploadManager = new UploadManager();
});