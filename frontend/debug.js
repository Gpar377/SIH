// Debug session and fix dashboard
console.log('=== SESSION DEBUG ===');
console.log('isAuthenticated:', sessionStorage.getItem('isAuthenticated'));
console.log('userRole:', sessionStorage.getItem('userRole'));
console.log('userCollege:', sessionStorage.getItem('userCollege'));
console.log('username:', sessionStorage.getItem('username'));

// Force set session for testing
if (!sessionStorage.getItem('userCollege')) {
    console.log('Setting test session...');
    sessionStorage.setItem('isAuthenticated', 'true');
    sessionStorage.setItem('userRole', 'college');
    sessionStorage.setItem('userCollege', 'gpj');
    sessionStorage.setItem('username', 'test');
}

// Override API calls to force college filter
if (window.API) {
    const originalGetDashboardStats = window.API.getDashboardStats;
    window.API.getDashboardStats = function() {
        const college = sessionStorage.getItem('userCollege');
        console.log('Dashboard API called with college:', college);
        return originalGetDashboardStats(college);
    };
    
    const originalGetStudents = window.API.getStudents;
    window.API.getStudents = function(params = {}) {
        const college = sessionStorage.getItem('userCollege');
        if (college && college !== 'government') {
            params.college_filter = college;
        }
        console.log('Students API called with params:', params);
        return originalGetStudents(params);
    };
}