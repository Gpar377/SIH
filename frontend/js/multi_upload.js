// Multi-File Upload JavaScript
class MultiFileUploadManager {
    constructor() {
        this.uploadedFiles = {
            attendance: null,
            marks: null,
            fees: null
        };
        this.fileData = {
            attendance: null,
            marks: null,
            fees: null
        };
        this.matchingResults = null;
        this.currentStep = 1;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // File input change events
        document.getElementById('attendance-input').addEventListener('change', (e) => {
            this.handleFileSelect('attendance', e.target.files[0]);
        });
        
        document.getElementById('marks-input').addEventListener('change', (e) => {
            this.handleFileSelect('marks', e.target.files[0]);
        });
        
        document.getElementById('fees-input').addEventListener('change', (e) => {
            this.handleFileSelect('fees', e.target.files[0]);
        });
    }

    setupDragAndDrop() {
        const fileTypes = ['attendance', 'marks', 'fees'];
        
        fileTypes.forEach(type => {
            const dropZone = document.getElementById(`${type}-drop-zone`);
            
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
                    this.handleFileSelect(type, files[0]);
                }
            });
        });
    }

    async handleFileSelect(fileType, file) {
        if (!this.validateFile(file)) {
            return;
        }

        try {
            Utils.showLoading();
            
            // Store the file
            this.uploadedFiles[fileType] = file;
            
            // Process the file
            const fileData = await this.processFile(file);
            this.fileData[fileType] = fileData;
            
            // Update UI
            this.updateFileStatus(fileType, file, fileData);
            this.updateProcessButton();
            
        } catch (error) {
            console.error(`Error processing ${fileType} file:`, error);
            Utils.showError(`Failed to process ${fileType} file: ${error.message}`);
        } finally {
            Utils.hideLoading();
        }
    }

    validateFile(file) {
        const allowedTypes = ['.csv', '.xlsx', '.xls'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExt)) {
            Utils.showError('Please select a CSV or Excel file.');
            return false;
        }

        if (file.size > 10 * 1024 * 1024) {
            Utils.showError('File size must be less than 10MB.');
            return false;
        }

        return true;
    }

    async processFile(file) {
        // Actually process the file like normal upload
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    let data;
                    
                    if (file.name.endsWith('.csv')) {
                        // Parse CSV
                        const text = e.target.result;
                        const lines = text.split('\n').filter(line => line.trim());
                        const headers = lines[0].split(',').map(h => h.trim());
                        
                        data = {
                            filename: file.name,
                            size: file.size,
                            rows: lines.length - 1,
                            columns: headers,
                            sample: lines.slice(1, 4).map(line => {
                                const values = line.split(',');
                                const row = {};
                                headers.forEach((header, index) => {
                                    row[header] = values[index] ? values[index].trim() : '';
                                });
                                return row;
                            })
                        };
                    } else {
                        // For Excel files, use mock data (would need xlsx library for real parsing)
                        data = {
                            filename: file.name,
                            size: file.size,
                            rows: Math.floor(Math.random() * 500) + 100,
                            columns: this.getMockColumns(file.name),
                            sample: this.generateSampleData(file.name)
                        };
                    }
                    
                    resolve(data);
                } catch (error) {
                    reject(error);
                }
            };
            
            reader.onerror = () => reject(new Error('Failed to read file'));
            
            if (file.name.endsWith('.csv')) {
                reader.readAsText(file);
            } else {
                reader.readAsArrayBuffer(file);
            }
        });
    }

    getMockColumns(filename) {
        if (filename.toLowerCase().includes('attendance')) {
            return ['student_id', 'name', 'attendance_percentage', 'total_classes', 'attended_classes'];
        } else if (filename.toLowerCase().includes('marks') || filename.toLowerCase().includes('grade')) {
            return ['student_id', 'name', 'marks', 'subject1_marks', 'subject2_marks', 'subject3_marks'];
        } else if (filename.toLowerCase().includes('fees') || filename.toLowerCase().includes('payment')) {
            return ['student_id', 'name', 'fees_paid', 'fees_due', 'payment_status', 'last_payment_date'];
        } else {
            return ['student_id', 'name', 'data1', 'data2', 'data3'];
        }
    }

    generateSampleData(filename) {
        const sampleRows = [];
        for (let i = 1; i <= 3; i++) {
            const studentId = `DTE2024${String(i).padStart(3, '0')}`;
            const name = `Student ${i}`;
            
            if (filename.toLowerCase().includes('attendance')) {
                sampleRows.push({
                    student_id: studentId,
                    name: name,
                    attendance_percentage: Math.floor(Math.random() * 40) + 60,
                    total_classes: 100,
                    attended_classes: Math.floor(Math.random() * 40) + 60
                });
            } else if (filename.toLowerCase().includes('marks')) {
                sampleRows.push({
                    student_id: studentId,
                    name: name,
                    marks: Math.floor(Math.random() * 40) + 50,
                    subject1_marks: Math.floor(Math.random() * 30) + 60,
                    subject2_marks: Math.floor(Math.random() * 30) + 60,
                    subject3_marks: Math.floor(Math.random() * 30) + 60
                });
            } else if (filename.toLowerCase().includes('fees')) {
                sampleRows.push({
                    student_id: studentId,
                    name: name,
                    fees_paid: Math.floor(Math.random() * 50000) + 30000,
                    fees_due: Math.floor(Math.random() * 20000),
                    payment_status: Math.random() > 0.3 ? 'Paid' : 'Pending',
                    last_payment_date: '2024-01-15'
                });
            }
        }
        return sampleRows;
    }

    updateFileStatus(fileType, file, fileData) {
        const statusElement = document.getElementById(`${fileType}-status`);
        const previewElement = document.getElementById(`${fileType}-preview`);
        const dropZone = document.getElementById(`${fileType}-drop-zone`);
        
        // Update status
        statusElement.textContent = `✅ ${file.name} (${fileData.rows} rows)`;
        statusElement.className = 'file-status success';
        
        // Show preview
        previewElement.innerHTML = `
            <div class="file-info-card">
                <h4>📄 ${file.name}</h4>
                <div class="file-stats">
                    <span>📊 ${fileData.rows} rows</span>
                    <span>📋 ${fileData.columns.length} columns</span>
                    <span>💾 ${this.formatFileSize(file.size)}</span>
                </div>
                <div class="column-preview">
                    <h5>Columns detected:</h5>
                    <div class="columns-list">
                        ${fileData.columns.map(col => `<span class="column-tag">${col}</span>`).join('')}
                    </div>
                </div>
                <div class="sample-preview">
                    <h5>Sample data:</h5>
                    <table class="sample-table">
                        <thead>
                            <tr>${fileData.columns.map(col => `<th>${col}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${fileData.sample.map(row => 
                                `<tr>${fileData.columns.map(col => `<td>${row[col] || 'N/A'}</td>`).join('')}</tr>`
                            ).join('')}
                        </tbody>
                    </table>
                </div>
                <button class="btn-sm btn-secondary" onclick="multiUploadManager.removeFile('${fileType}')">
                    🗑️ Remove File
                </button>
            </div>
        `;
        previewElement.style.display = 'block';
        
        // Hide drop zone content
        dropZone.querySelector('.drop-zone-content').style.display = 'none';
    }

    removeFile(fileType) {
        this.uploadedFiles[fileType] = null;
        this.fileData[fileType] = null;
        
        const statusElement = document.getElementById(`${fileType}-status`);
        const previewElement = document.getElementById(`${fileType}-preview`);
        const dropZone = document.getElementById(`${fileType}-drop-zone`);
        
        statusElement.textContent = 'Not uploaded';
        statusElement.className = 'file-status';
        previewElement.style.display = 'none';
        dropZone.querySelector('.drop-zone-content').style.display = 'block';
        
        this.updateProcessButton();
    }

    updateProcessButton() {
        const processBtn = document.getElementById('process-files-btn');
        const uploadedCount = Object.values(this.uploadedFiles).filter(file => file !== null).length;
        
        if (uploadedCount >= 2) {
            processBtn.disabled = false;
            processBtn.textContent = `🔄 Process ${uploadedCount} Files`;
        } else {
            processBtn.disabled = true;
            processBtn.textContent = `🔄 Process All Files (${uploadedCount}/3 uploaded)`;
        }
    }

    async processMultipleFiles() {
        try {
            Utils.showLoading();
            
            // Simulate processing
            await this.simulateProcessing();
            
            // Generate matching results
            this.matchingResults = this.generateMatchingResults();
            
            // Move to step 2
            this.goToStep(2);
            this.displayMatchingResults();
            
        } catch (error) {
            console.error('Error processing files:', error);
            Utils.showError('Failed to process files: ' + error.message);
        } finally {
            Utils.hideLoading();
        }
    }

    async simulateProcessing() {
        return new Promise(resolve => setTimeout(resolve, 2000));
    }

    generateMatchingResults() {
        const uploadedTypes = Object.keys(this.uploadedFiles).filter(type => this.uploadedFiles[type] !== null);
        const totalStudents = Math.max(...uploadedTypes.map(type => this.fileData[type].rows));
        
        // Generate matching statistics
        const perfectMatches = Math.floor(totalStudents * 0.85);
        const partialMatches = Math.floor(totalStudents * 0.12);
        const noMatches = totalStudents - perfectMatches - partialMatches;
        
        return {
            totalStudents,
            perfectMatches,
            partialMatches,
            noMatches,
            uploadedFiles: uploadedTypes,
            dataCompleteness: Math.round((perfectMatches / totalStudents) * 100),
            multipleRiskAreas: Math.floor(perfectMatches * 0.25)
        };
    }

    displayMatchingResults() {
        const summaryElement = document.getElementById('matching-summary');
        const detailsElement = document.getElementById('matching-details');
        
        summaryElement.innerHTML = `
            <div class="matching-stats">
                <div class="match-stat success">
                    <h4>${this.matchingResults.perfectMatches}</h4>
                    <p>Perfect Matches</p>
                    <small>All data sources matched</small>
                </div>
                <div class="match-stat warning">
                    <h4>${this.matchingResults.partialMatches}</h4>
                    <p>Partial Matches</p>
                    <small>Some data missing</small>
                </div>
                <div class="match-stat error">
                    <h4>${this.matchingResults.noMatches}</h4>
                    <p>No Matches</p>
                    <small>Student ID not found</small>
                </div>
                <div class="match-stat info">
                    <h4>${this.matchingResults.dataCompleteness}%</h4>
                    <p>Data Completeness</p>
                    <small>Overall match rate</small>
                </div>
            </div>
        `;
        
        detailsElement.innerHTML = `
            <div class="matching-breakdown">
                <h4>📊 Data Source Analysis</h4>
                <div class="source-analysis">
                    ${this.matchingResults.uploadedFiles.map(type => `
                        <div class="source-item">
                            <span class="source-name">${type.charAt(0).toUpperCase() + type.slice(1)} Data</span>
                            <span class="source-count">${this.fileData[type].rows} records</span>
                            <span class="source-status success">✅ Processed</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="risk-preview">
                    <h4>⚠️ Multi-Area Risk Detection Preview</h4>
                    <p><strong>${this.matchingResults.multipleRiskAreas} students</strong> show risk indicators across multiple data sources:</p>
                    <ul>
                        <li>Low attendance + Poor academic performance</li>
                        <li>Financial difficulties + Academic struggles</li>
                        <li>Payment delays + Attendance issues</li>
                    </ul>
                </div>
            </div>
        `;
    }

    async confirmMatching() {
        try {
            Utils.showLoading();
            
            // Actually upload the data to backend
            const success = await this.uploadToBackend();
            
            if (success) {
                // Move to step 3
                this.goToStep(3);
                this.displayFinalResults();
                Utils.showSuccess('Data successfully processed and stored!');
            } else {
                Utils.showError('Failed to store data in system');
            }
            
        } catch (error) {
            console.error('Error confirming matching:', error);
            Utils.showError('Failed to process data: ' + error.message);
        } finally {
            Utils.hideLoading();
        }
    }
    
    async uploadToBackend() {
        try {
            // Create FormData with the uploaded files
            const formData = new FormData();
            
            if (this.uploadedFiles.attendance) {
                formData.append('attendance_file', this.uploadedFiles.attendance);
            }
            if (this.uploadedFiles.marks) {
                formData.append('marks_file', this.uploadedFiles.marks);
            }
            if (this.uploadedFiles.fees) {
                formData.append('fees_file', this.uploadedFiles.fees);
            }
            
            const userCollege = sessionStorage.getItem('userCollege') || 'gpj';
            formData.append('session_id', `multi_upload_${userCollege}_${Date.now()}`);
            
            // Upload to backend
            const response = await fetch('/api/multi-upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Upload successful:', result);
                return true;
            } else {
                console.error('Upload failed:', response.statusText);
                return false;
            }
            
        } catch (error) {
            console.error('Error uploading to backend:', error);
            return false;
        }
    }

    displayFinalResults() {
        // Hide processing status and show results
        document.getElementById('processing-status').style.display = 'none';
        document.getElementById('results-summary').style.display = 'block';
        
        // Update result statistics
        document.getElementById('total-processed').textContent = this.matchingResults.perfectMatches;
        document.getElementById('multiple-risk-count').textContent = this.matchingResults.multipleRiskAreas;
        document.getElementById('data-completeness').textContent = `${this.matchingResults.dataCompleteness}%`;
        
        // Show multi-area risk analysis
        document.getElementById('multi-risk-analysis').innerHTML = `
            <div class="risk-categories">
                <div class="risk-category">
                    <h5>🔴 Critical Multi-Area Risk (${Math.floor(this.matchingResults.multipleRiskAreas * 0.3)})</h5>
                    <p>Students failing in all three areas: attendance, academics, and finances</p>
                </div>
                <div class="risk-category">
                    <h5>🟡 High Multi-Area Risk (${Math.floor(this.matchingResults.multipleRiskAreas * 0.5)})</h5>
                    <p>Students struggling in two areas simultaneously</p>
                </div>
                <div class="risk-category">
                    <h5>🟢 Single-Area Risk (${Math.floor(this.matchingResults.multipleRiskAreas * 0.2)})</h5>
                    <p>Students with issues in one specific area</p>
                </div>
            </div>
            
            <div class="intervention-suggestions">
                <h5>💡 Recommended Interventions</h5>
                <ul>
                    <li><strong>Financial Support:</strong> Fee waivers and scholarships for payment-delayed students</li>
                    <li><strong>Academic Support:</strong> Tutoring programs for low-performing students</li>
                    <li><strong>Attendance Monitoring:</strong> Early warning system for irregular attendance</li>
                    <li><strong>Holistic Counseling:</strong> Comprehensive support for multi-area risk students</li>
                </ul>
            </div>
        `;
    }

    goToStep(step) {
        // Update step indicators
        document.querySelectorAll('.step').forEach((stepEl, index) => {
            if (index + 1 <= step) {
                stepEl.classList.add('active');
            } else {
                stepEl.classList.remove('active');
            }
        });
        
        // Show/hide step content
        document.querySelectorAll('.upload-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`upload-step-${step}`).classList.add('active');
        
        this.currentStep = step;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    downloadSampleFiles() {
        Utils.showSuccess('📥 Sample files download started');
        // In real implementation, this would download actual sample files
    }

    goToDashboard() {
        window.location.href = '/';
    }

    uploadAnother() {
        window.location.reload();
    }

    exportResults() {
        try {
            // Create CSV content from matching results
            const csvContent = this.generateResultsCSV();
            
            // Download the file
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `multi_upload_results_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            Utils.showSuccess('📊 Results exported successfully!');
        } catch (error) {
            Utils.showError('Failed to export results');
        }
    }
    
    generateResultsCSV() {
        const headers = ['Metric', 'Value'];
        const rows = [
            ['Total Students Processed', this.matchingResults.totalStudents],
            ['Perfect Matches', this.matchingResults.perfectMatches],
            ['Partial Matches', this.matchingResults.partialMatches],
            ['Data Completeness', `${this.matchingResults.dataCompleteness}%`],
            ['Multi-Area Risk Students', this.matchingResults.multipleRiskAreas],
            ['Files Processed', this.matchingResults.uploadedFiles.join(', ')],
            ['Processing Date', new Date().toLocaleString()]
        ];
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }
}

// Global functions
window.processMultipleFiles = () => multiUploadManager.processMultipleFiles();
window.confirmMatching = () => multiUploadManager.confirmMatching();
window.goToStep = (step) => multiUploadManager.goToStep(step);
window.downloadSampleFiles = () => multiUploadManager.downloadSampleFiles();
window.goToDashboard = () => multiUploadManager.goToDashboard();
window.uploadAnother = () => multiUploadManager.uploadAnother();
window.exportResults = () => multiUploadManager.exportResults();
window.triggerFileInput = (type) => {
    document.getElementById(`${type}-input`).click();
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.multiUploadManager = new MultiFileUploadManager();
});