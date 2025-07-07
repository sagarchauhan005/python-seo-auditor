// SEO Audit Tool JavaScript

// Configuration
const CONFIG = {
    API_BASE_URL: '/api/audit',
    TIMEOUT: 30000,
    PROGRESS_STEPS: [
        'Fetching page content...',
        'Analyzing HTML structure...',
        'Checking meta tags...',
        'Analyzing content...',
        'Checking links...',
        'Finalizing report...'
    ]
};

// SEO Check definitions
const SEO_CHECKS = {
    title_tag: {
        name: 'Title Tag',
        description: 'Check if page has a proper title tag with optimal length',
        icon: 'fas fa-heading'
    },
    meta_description: {
        name: 'Meta Description',
        description: 'Verify presence and length of meta description',
        icon: 'fas fa-align-left'
    },
    h1_tag: {
        name: 'H1 Tag',
        description: 'Check for presence and uniqueness of H1 tag',
        icon: 'fas fa-text-height'
    },
    header_hierarchy: {
        name: 'Header Hierarchy',
        description: 'Analyze proper H1-H6 header structure',
        icon: 'fas fa-sitemap'
    },
    content_length: {
        name: 'Content Length',
        description: 'Evaluate content length and readability',
        icon: 'fas fa-file-text'
    },
    keyword_density: {
        name: 'Keyword Density',
        description: 'Analyze keyword distribution and density',
        icon: 'fas fa-search'
    },
    alt_text: {
        name: 'Image Alt Text',
        description: 'Check if images have proper alt attributes',
        icon: 'fas fa-image'
    },
    canonical_url: {
        name: 'Canonical URL',
        description: 'Verify presence of canonical link tag',
        icon: 'fas fa-link'
    },
    meta_robots: {
        name: 'Meta Robots',
        description: 'Check for meta robots tag configuration',
        icon: 'fas fa-robot'
    },
    xml_sitemap: {
        name: 'XML Sitemap',
        description: 'Look for XML sitemap reference',
        icon: 'fas fa-map'
    },
    schema_markup: {
        name: 'Schema Markup',
        description: 'Detect structured data markup',
        icon: 'fas fa-code'
    },
    broken_links: {
        name: 'Broken Links',
        description: 'Check for broken internal and external links',
        icon: 'fas fa-unlink'
    }
};

// DOM Elements
let elements = {};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
});

// Initialize DOM element references
function initializeElements() {
    elements = {
        auditForm: document.getElementById('auditForm'),
        urlInput: document.getElementById('urlInput'),
        submitBtn: document.getElementById('submitBtn'),
        errorMessage: document.getElementById('errorMessage'),
        loadingContainer: document.getElementById('loadingContainer'),
        loadingStatus: document.getElementById('loadingStatus'),
        progressFill: document.getElementById('progressFill'),
        resultsContainer: document.getElementById('resultsContainer'),
        overallScoreValue: document.getElementById('overallScoreValue'),
        auditedUrl: document.getElementById('auditedUrl'),
        auditTimestamp: document.getElementById('auditTimestamp'),
        passedCount: document.getElementById('passedCount'),
        failedCount: document.getElementById('failedCount'),
        checksGrid: document.getElementById('checksGrid'),
        failedChecksSection: document.getElementById('failedChecksSection'),
        failedChecksList: document.getElementById('failedChecksList'),
        statsGrid: document.getElementById('statsGrid'),
        exportBtn: document.getElementById('exportBtn'),
        newAuditBtn: document.getElementById('newAuditBtn')
    };
}

// Setup event listeners
function setupEventListeners() {
    elements.auditForm.addEventListener('submit', handleFormSubmit);
    elements.exportBtn.addEventListener('click', exportReport);
    elements.newAuditBtn.addEventListener('click', startNewAudit);
    elements.urlInput.addEventListener('input', clearErrors);
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();

    const url = elements.urlInput.value.trim();

    if (!validateUrl(url)) {
        showError('Please enter a valid URL (e.g., https://example.com)');
        return;
    }

    clearErrors();
    await performAudit(url);
}

// Validate URL format
function validateUrl(url) {
    const urlPattern = /^https?:\/\/.+\..+/;
    return urlPattern.test(url);
}

// Show error message
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.classList.add('show');
}

// Clear error messages
function clearErrors() {
    elements.errorMessage.classList.remove('show');
}

// Perform SEO audit
async function performAudit(url) {
    showLoadingState();
    hideResults();

    try {
        const response = await callAuditAPI(url);

        if (response.status === 'success') {
            displayResults(response.data);
        } else {
            throw new Error(response.message || 'Audit failed');
        }

    } catch (error) {
        console.error('Audit error:', error);
        showError(`Audit failed: ${error.message}`);
    } finally {
        hideLoadingState();
    }
}

// Call the audit API
async function callAuditAPI(url) {
    const requestData = {
        url: url,
        timestamp: new Date().toISOString()
    };

    // Simulate progress updates
    simulateProgress();

    try {
        const response = await fetch(CONFIG.API_BASE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(requestData),
            timeout: CONFIG.TIMEOUT
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();

    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error('Network error - please check your connection');
        }
        throw error;
    }
}

// Get CSRF token for Django
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// Simulate progress during audit
function simulateProgress() {
    let progress = 0;
    let stepIndex = 0;

    const progressInterval = setInterval(() => {
        progress += Math.random() * 15 + 5;

        if (progress >= 100) {
            progress = 100;
            clearInterval(progressInterval);
        }

        elements.progressFill.style.width = `${progress}%`;

        // Update status message
        if (stepIndex < CONFIG.PROGRESS_STEPS.length - 1 && progress > (stepIndex + 1) * (100 / CONFIG.PROGRESS_STEPS.length)) {
            stepIndex++;
            elements.loadingStatus.textContent = CONFIG.PROGRESS_STEPS[stepIndex];
        }
    }, 500);
}

// Show loading state
function showLoadingState() {
    elements.submitBtn.disabled = true;
    elements.loadingContainer.style.display = 'block';
    elements.progressFill.style.width = '0%';
    elements.loadingStatus.textContent = CONFIG.PROGRESS_STEPS[0];
}

// Hide loading state
function hideLoadingState() {
    elements.submitBtn.disabled = false;
    elements.loadingContainer.style.display = 'none';
}

// Hide results container
function hideResults() {
    elements.resultsContainer.style.display = 'none';
}

// Display audit results
function displayResults(data) {
    // Update overall score
    const score = calculateOverallScore(data.checks);
    elements.overallScoreValue.textContent = score.passed;

    // Update URL and timestamp
    elements.auditedUrl.textContent = data.url;
    elements.auditTimestamp.textContent = `Analyzed on ${formatDate(data.timestamp)}`;

    // Update score breakdown
    elements.passedCount.textContent = `${score.passed} passed`;
    elements.failedCount.textContent = `${score.failed} failed`;

    // Display SEO checks
    displaySEOChecks(data.checks);

    // Display failed checks details
    displayFailedChecks(data.checks);

    // Display page statistics
    displayPageStatistics(data.page_info);

    // Show results
    elements.resultsContainer.style.display = 'block';

    // Scroll to results
    elements.resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Calculate overall score
function calculateOverallScore(checks) {
    const passed = Object.values(checks).filter(check => check.status === 'passed').length;
    const failed = Object.values(checks).filter(check => check.status === 'failed').length;

    return { passed, failed, total: passed + failed };
}

// Display SEO checks grid
function displaySEOChecks(checks) {
    elements.checksGrid.innerHTML = '';

    Object.keys(SEO_CHECKS).forEach(checkKey => {
        const checkData = checks[checkKey];
        const checkConfig = SEO_CHECKS[checkKey];

        if (!checkData) return;

        const checkElement = createCheckElement(checkKey, checkData, checkConfig);
        elements.checksGrid.appendChild(checkElement);
    });
}

// Create individual check element
function createCheckElement(checkKey, checkData, checkConfig) {
    const div = document.createElement('div');
    div.className = `check-item ${checkData.status}`;
    div.setAttribute('data-check', checkKey);

    const isPassed = checkData.status === 'passed';
    const iconClass = isPassed ? 'fas fa-check' : 'fas fa-times';

    div.innerHTML = `
        <div class="check-header">
            <div class="check-icon">
                <i class="${iconClass}"></i>
            </div>
            <div class="check-title">${checkConfig.name}</div>
        </div>
        <div class="check-description">${checkConfig.description}</div>
        ${checkData.details ? `<div class="check-details">${checkData.details}</div>` : ''}
    `;

    return div;
}

// Display failed checks with detailed information
function displayFailedChecks(checks) {
    const failedChecks = Object.entries(checks).filter(([key, check]) => check.status === 'failed');

    if (failedChecks.length === 0) {
        elements.failedChecksSection.style.display = 'none';
        return;
    }

    elements.failedChecksSection.style.display = 'block';
    elements.failedChecksList.innerHTML = '';

    failedChecks.forEach(([checkKey, checkData]) => {
        const checkConfig = SEO_CHECKS[checkKey];
        const failedElement = createFailedCheckElement(checkKey, checkData, checkConfig);
        elements.failedChecksList.appendChild(failedElement);
    });
}

// Create failed check element with recommendations
function createFailedCheckElement(checkKey, checkData, checkConfig) {
    const div = document.createElement('div');
    div.className = 'failed-check-item';

    div.innerHTML = `
        <div class="failed-check-header">
            <i class="failed-check-icon fas fa-exclamation-triangle"></i>
            <div class="failed-check-title">${checkConfig.name}</div>
        </div>
        <div class="failed-check-description">
            ${checkData.issue || checkConfig.description}
        </div>
        ${checkData.recommendation ? `
            <div class="failed-check-recommendation">
                <strong>Recommendation:</strong> ${checkData.recommendation}
            </div>
        ` : ''}
    `;

    return div;
}

// Display page statistics
function displayPageStatistics(pageInfo) {
    elements.statsGrid.innerHTML = '';

    const stats = [
        { label: 'Page Title Length', value: pageInfo.title_length || 'N/A', unit: 'chars' },
        { label: 'Meta Description Length', value: pageInfo.meta_description_length || 'N/A', unit: 'chars' },
        { label: 'Word Count', value: pageInfo.word_count || 'N/A', unit: 'words' },
        { label: 'Images Found', value: pageInfo.images_count || 'N/A', unit: 'images' },
        { label: 'Internal Links', value: pageInfo.internal_links || 'N/A', unit: 'links' },
        { label: 'External Links', value: pageInfo.external_links || 'N/A', unit: 'links' },
        { label: 'H1 Tags', value: pageInfo.h1_count || 'N/A', unit: 'tags' },
        { label: 'Load Time', value: pageInfo.load_time || 'N/A', unit: 'seconds' }
    ];

    stats.forEach(stat => {
        const statElement = createStatElement(stat);
        elements.statsGrid.appendChild(statElement);
    });
}

// Create individual stat element
function createStatElement(stat) {
    const div = document.createElement('div');
    div.className = 'stat-item';

    const displayValue = stat.value !== 'N/A' ? `${stat.value}` : stat.value;

    div.innerHTML = `
        <span class="stat-value">${displayValue}</span>
        <span class="stat-label">${stat.label}</span>
    `;

    return div;
}

// Export report functionality
function exportReport() {
    const reportData = gatherReportData();

    if (!reportData) {
        showError('No audit data available to export');
        return;
    }

    const reportText = generateReportText(reportData);
    downloadTextFile(reportText, `seo-audit-${formatDateForFilename(new Date())}.txt`);
}

// Gather current report data
function gatherReportData() {
    const urlElement = elements.auditedUrl;
    const timestampElement = elements.auditTimestamp;

    if (!urlElement.textContent) {
        return null;
    }

    return {
        url: urlElement.textContent,
        timestamp: timestampElement.textContent,
        score: {
            passed: parseInt(elements.passedCount.textContent.split(' ')[0]),
            failed: parseInt(elements.failedCount.textContent.split(' ')[0])
        },
        checks: gatherCheckResults(),
        stats: gatherPageStats()
    };
}

// Gather check results from DOM
function gatherCheckResults() {
    const checkElements = elements.checksGrid.querySelectorAll('.check-item');
    const results = {};

    checkElements.forEach(element => {
        const checkKey = element.getAttribute('data-check');
        const status = element.classList.contains('passed') ? 'passed' : 'failed';
        const title = element.querySelector('.check-title').textContent;
        const description = element.querySelector('.check-description').textContent;
        const details = element.querySelector('.check-details')?.textContent || '';

        results[checkKey] = {
            title,
            description,
            status,
            details
        };
    });

    return results;
}

// Gather page statistics from DOM
function gatherPageStats() {
    const statElements = elements.statsGrid.querySelectorAll('.stat-item');
    const stats = {};

    statElements.forEach(element => {
        const label = element.querySelector('.stat-label').textContent;
        const value = element.querySelector('.stat-value').textContent;
        stats[label] = value;
    });

    return stats;
}

// Generate report text
function generateReportText(data) {
    let report = '';

    report += '='.repeat(60) + '\n';
    report += '                    SEO AUDIT REPORT\n';
    report += '='.repeat(60) + '\n\n';

    report += `URL: ${data.url}\n`;
    report += `Date: ${data.timestamp}\n`;
    report += `Overall Score: ${data.score.passed}/${data.score.passed + data.score.failed}\n\n`;

    report += 'SEO CHECK RESULTS:\n';
    report += '-'.repeat(30) + '\n';

    Object.entries(data.checks).forEach(([key, check]) => {
        const status = check.status.toUpperCase();
        const statusIcon = check.status === 'passed' ? '✓' : '✗';

        report += `${statusIcon} ${check.title}: ${status}\n`;
        if (check.details) {
            report += `   Details: ${check.details}\n`;
        }
        report += '\n';
    });

    report += 'PAGE STATISTICS:\n';
    report += '-'.repeat(30) + '\n';

    Object.entries(data.stats).forEach(([label, value]) => {
        report += `${label}: ${value}\n`;
    });

    report += '\n' + '='.repeat(60) + '\n';
    report += 'Report generated by SEO Audit Tool\n';

    return report;
}

// Download text file
function downloadTextFile(content, filename) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = url;
    a.download = filename;
    a.style.display = 'none';

    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    window.URL.revokeObjectURL(url);
}

// Start new audit
function startNewAudit() {
    // Clear form
    elements.urlInput.value = '';
    elements.urlInput.focus();

    // Clear errors
    clearErrors();

    // Hide results
    hideResults();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format date for filename
function formatDateForFilename(date) {
    return date.toISOString().split('T')[0];
}

// Utility function to handle API timeouts
function withTimeout(promise, ms) {
    return Promise.race([
        promise,
        new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Request timeout')), ms)
        )
    ]);
}

// Example response structure for testing (remove in production)
const EXAMPLE_RESPONSE = {
    status: 'success',
    data: {
        url: 'https://example.com',
        timestamp: new Date().toISOString(),
        checks: {
            title_tag: {
                status: 'passed',
                details: 'Title tag present with 45 characters'
            },
            meta_description: {
                status: 'failed',
                details: 'Meta description missing',
                issue: 'No meta description tag found on the page',
                recommendation: 'Add a compelling meta description between 150-160 characters that accurately describes the page content'
            },
            h1_tag: {
                status: 'passed',
                details: 'Single H1 tag found with appropriate length'
            },
            header_hierarchy: {
                status: 'passed',
                details: 'Proper header hierarchy maintained (H1 → H2 → H3)'
            },
            content_length: {
                status: 'passed',
                details: 'Content length is 850 words - good for SEO'
            },
            keyword_density: {
                status: 'failed',
                details: 'Keyword density appears unoptimized',
                issue: 'Primary keyword density is too low (0.5%)',
                recommendation: 'Increase keyword density to 1-2% by naturally incorporating target keywords'
            },
            alt_text: {
                status: 'failed',
                details: '3 out of 8 images missing alt text',
                issue: 'Several images lack descriptive alt attributes',
                recommendation: 'Add descriptive alt text to all images for better accessibility and SEO'
            },
            canonical_url: {
                status: 'passed',
                details: 'Canonical URL properly set'
            },
            meta_robots: {
                status: 'passed',
                details: 'Meta robots tag configured correctly'
            },
            xml_sitemap: {
                status: 'failed',
                details: 'XML sitemap reference not found',
                issue: 'No XML sitemap linked in robots.txt or HTML',
                recommendation: 'Create and submit an XML sitemap to search engines'
            },
            schema_markup: {
                status: 'failed',
                details: 'No structured data detected',
                issue: 'No JSON-LD or microdata schema markup found',
                recommendation: 'Implement relevant schema markup (Organization, Article, etc.) to enhance search results'
            },
            broken_links: {
                status: 'passed',
                details: 'No broken links detected'
            }
        },
        page_info: {
            title_length: 45,
            meta_description_length: 0,
            word_count: 850,
            images_count: 8,
            internal_links: 12,
            external_links: 5,
            h1_count: 1,
            load_time: 2.3
        }
    }
};

// For development/testing - remove in production
// if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
//     console.log('Development mode: Using example response');
//
//     // Override API call for testing
//     const originalCallAuditAPI = callAuditAPI;
//     callAuditAPI = async function(url) {
//         // Simulate API delay
//         await new Promise(resolve => setTimeout(resolve, 3000));
//
//         // Return example response with the provided URL
//         const response = { ...EXAMPLE_RESPONSE };
//         response.data.url = url;
//         return response;
//     };
// }