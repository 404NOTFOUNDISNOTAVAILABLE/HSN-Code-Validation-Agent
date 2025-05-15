// Main JavaScript file for HSN Code Validator

document.addEventListener('DOMContentLoaded', function() {
    // Function to handle API-based validation
    const validateAPI = async (hsn_codes, include_hierarchy = false) => {
        try {
            const response = await fetch('/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    hsn_codes: hsn_codes,
                    include_hierarchy: include_hierarchy
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error validating HSN codes:', error);
            return {
                response_type: 'error',
                message: 'Failed to validate HSN codes. Please try again.'
            };
        }
    };

    // Handle form submission for API usage (for future enhancements)
    const apiForm = document.getElementById('api-form');
    if (apiForm) {
        apiForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const hsnCodes = document.getElementById('api-hsn-codes').value;
            const includeHierarchy = document.getElementById('api-include-hierarchy').checked;
            
            const resultDiv = document.getElementById('api-result');
            resultDiv.innerHTML = '<div class="loading">Processing...</div>';
            
            const result = await validateAPI(hsnCodes, includeHierarchy);
            displayAPIResult(result, resultDiv);
        });
    }
    
    // Function to display API results
    const displayAPIResult = (result, container) => {
        if (!container) return;
        
        let html = '';
        
        if (result.response_type === 'error') {
            html = `<div class="card error">
                <h3>Error</h3>
                <p>${result.message}</p>
            </div>`;
        } else if (result.response_type === 'valid_hsn' || result.response_type === 'invalid_hsn') {
            const isValid = result.response_type === 'valid_hsn';
            html = `<div class="card ${isValid ? 'success' : 'error'}">
                <h3>${isValid ? 'Valid' : 'Invalid'} HSN Code</h3>
                <div class="result">
                    <div class="code">${result.code}</div>
                    <div class="${isValid ? 'description' : 'reason'}">${isValid ? result.description : result.reason}</div>
                </div>
            </div>`;
        } else if (result.response_type === 'multiple_hsn_results') {
            html = `<div class="card summary">
                <h3>Validation Summary</h3>
                <p>${result.summary}</p>
            </div>`;
            
            // Add detailed results table
            html += `<div class="card">
                <h3>Detailed Results</h3>
                <table>
                    <thead>
                        <tr>
                            <th>HSN Code</th>
                            <th>Status</th>
                            <th>Description / Reason</th>
                        </tr>
                    </thead>
                    <tbody>`;
                    
            result.results.results.forEach(item => {
                html += `<tr class="${item.valid ? 'valid' : 'invalid'}">
                    <td>${item.code}</td>
                    <td>${item.valid ? 'Valid' : 'Invalid'}</td>
                    <td>${item.valid ? item.description : item.reason}</td>
                </tr>`;
            });
            
            html += `</tbody></table></div>`;
        }
        
        container.innerHTML = html;
    };
    
    // Add copy to clipboard functionality for code examples
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const codeElement = this.previousElementSibling;
            const text = codeElement.textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    });
});