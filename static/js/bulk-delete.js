/**
 * Bulk Delete Functionality for Questions
 */

// Track selected questions
let selectedQuestions = new Set();

// Initialize bulk delete functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeBulkDelete();
});

function initializeBulkDelete() {
    // Add checkboxes to question items
    addCheckboxesToQuestions();
    
    // Add bulk action toolbar
    addBulkActionToolbar();
    
    // Handle checkbox changes
    handleCheckboxChanges();
}

function addCheckboxesToQuestions() {
    const questionItems = document.querySelectorAll('.question-list-item');
    
    questionItems.forEach(function(item, index) {
        // Only add checkboxes to user's own questions
        const deleteButton = item.querySelector('a[href*="/delete/"]');
        if (!deleteButton) return; // Skip if user can't delete this question
        
        const questionId = extractQuestionId(deleteButton.href);
        if (!questionId) return;
        
        // Create checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'form-check-input question-checkbox me-2';
        checkbox.value = questionId;
        checkbox.id = `question-${questionId}`;
        
        // Add checkbox to the beginning of the question item
        const cardBody = item.querySelector('.card-body');
        if (cardBody) {
            const firstChild = cardBody.firstChild;
            cardBody.insertBefore(checkbox, firstChild);
        }
    });
}

function addBulkActionToolbar() {
    const questionsSection = document.querySelector('.card-header');
    if (!questionsSection) return;
    
    // Create bulk action toolbar
    const toolbar = document.createElement('div');
    toolbar.id = 'bulk-action-toolbar';
    toolbar.className = 'alert alert-info mt-3';
    toolbar.style.display = 'none';
    toolbar.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <i class="fas fa-check-square me-2"></i>
                <span id="selected-count">0</span> question(s) selected
            </div>
            <div>
                <button type="button" class="btn btn-sm btn-outline-primary me-2" onclick="selectAllQuestions()">
                    <i class="fas fa-check-double"></i> Select All
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary me-2" onclick="clearSelection()">
                    <i class="fas fa-times"></i> Clear
                </button>
                <button type="button" class="btn btn-sm btn-danger" onclick="bulkDeleteQuestions()">
                    <i class="fas fa-trash"></i> Delete Selected
                </button>
            </div>
        </div>
    `;
    
    // Insert toolbar after the card header
    questionsSection.parentNode.insertBefore(toolbar, questionsSection.nextSibling);
}

function handleCheckboxChanges() {
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('question-checkbox')) {
            const questionId = e.target.value;
            
            if (e.target.checked) {
                selectedQuestions.add(questionId);
            } else {
                selectedQuestions.delete(questionId);
            }
            
            updateBulkActionToolbar();
        }
    });
}

function updateBulkActionToolbar() {
    const toolbar = document.getElementById('bulk-action-toolbar');
    const countSpan = document.getElementById('selected-count');
    
    if (!toolbar || !countSpan) return;
    
    const count = selectedQuestions.size;
    countSpan.textContent = count;
    
    if (count > 0) {
        toolbar.style.display = 'block';
    } else {
        toolbar.style.display = 'none';
    }
}

function selectAllQuestions() {
    const checkboxes = document.querySelectorAll('.question-checkbox');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = true;
        selectedQuestions.add(checkbox.value);
    });
    updateBulkActionToolbar();
}

function clearSelection() {
    const checkboxes = document.querySelectorAll('.question-checkbox');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = false;
    });
    selectedQuestions.clear();
    updateBulkActionToolbar();
}

function bulkDeleteQuestions() {
    if (selectedQuestions.size === 0) {
        alert('Please select at least one question to delete.');
        return;
    }
    
    const count = selectedQuestions.size;
    const confirmMessage = `Are you sure you want to delete ${count} question${count > 1 ? 's' : ''}? This action cannot be undone.`;
    
    if (!confirm(confirmMessage)) {
        return;
    }
    
    // Show loading state
    const deleteButton = document.querySelector('#bulk-action-toolbar .btn-danger');
    const originalText = deleteButton.innerHTML;
    deleteButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
    deleteButton.disabled = true;
    
    // Delete questions one by one
    const questionIds = Array.from(selectedQuestions);
    deleteQuestionsSequentially(questionIds, 0, function() {
        // Reload page after all deletions
        window.location.reload();
    });
}

function deleteQuestionsSequentially(questionIds, index, callback) {
    if (index >= questionIds.length) {
        callback();
        return;
    }
    
    const questionId = questionIds[index];
    
    // Create a form and submit it
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/question/${questionId}/delete/`;
    form.style.display = 'none';
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken.value;
        form.appendChild(csrfInput);
    }
    
    document.body.appendChild(form);
    
    // Submit form using fetch to avoid page redirect
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        document.body.removeChild(form);
        // Continue with next question
        deleteQuestionsSequentially(questionIds, index + 1, callback);
    })
    .catch(error => {
        console.error('Error deleting question:', error);
        document.body.removeChild(form);
        // Continue with next question even if one fails
        deleteQuestionsSequentially(questionIds, index + 1, callback);
    });
}

function extractQuestionId(url) {
    const match = url.match(/\/question\/(\d+)\/delete\//);
    return match ? match[1] : null;
}

// Toggle bulk delete mode
function toggleBulkDeleteMode() {
    const checkboxes = document.querySelectorAll('.question-checkbox');
    const toolbar = document.getElementById('bulk-action-toolbar');
    
    if (checkboxes.length > 0) {
        // Hide bulk delete mode
        checkboxes.forEach(cb => cb.style.display = 'none');
        if (toolbar) toolbar.style.display = 'none';
        selectedQuestions.clear();
    } else {
        // Show bulk delete mode
        addCheckboxesToQuestions();
        addBulkActionToolbar();
    }
}
