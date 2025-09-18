// Enhanced Product Search and Filters
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('product-search');
    const productsContainer = document.getElementById('products-container');
    const productCards = document.querySelectorAll('.product-card');
    
    // Live Search Functionality
    if (searchInput && productCards.length > 0) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            productCards.forEach(card => {
                const title = card.querySelector('.product-title')?.textContent.toLowerCase() || '';
                const description = card.querySelector('.product-description')?.textContent.toLowerCase() || '';
                const category = card.querySelector('.product-category')?.textContent.toLowerCase() || '';
                
                const matches = title.includes(searchTerm) || 
                              description.includes(searchTerm) || 
                              category.includes(searchTerm);
                
                if (matches || searchTerm === '') {
                    card.style.display = 'flex';
                    card.style.animation = 'fadeIn 0.3s ease';
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Show/hide empty state
            const visibleCards = Array.from(productCards).filter(card => 
                card.style.display !== 'none'
            );
            
            if (visibleCards.length === 0 && searchTerm !== '') {
                showEmptySearchState(searchTerm);
            } else {
                hideEmptySearchState();
            }
        });
    }
    
    // File Upload Enhancement
    const fileInput = document.getElementById('image');
    const fileUploadArea = document.querySelector('.file-upload-area');
    
    if (fileInput && fileUploadArea) {
        // Drag and Drop functionality
        fileUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        fileUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        fileUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileUploadDisplay(files[0]);
            }
        });
        
        // File selection
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                updateFileUploadDisplay(this.files[0]);
            }
        });
    }
    
    function updateFileUploadDisplay(file) {
        const fileUploadContent = document.querySelector('.file-upload-content');
        if (fileUploadContent) {
            fileUploadContent.innerHTML = `
                <i class="fas fa-check-circle" style="color: #28a745;"></i>
                <p>تم اختيار الملف: ${file.name}</p>
                <small>الحجم: ${(file.size / (1024 * 1024)).toFixed(2)} MB</small>
            `;
        }
    }
    
    function showEmptySearchState(searchTerm) {
        let emptyState = document.querySelector('.search-empty-state');
        if (!emptyState) {
            emptyState = document.createElement('div');
            emptyState.className = 'search-empty-state empty-state';
            emptyState.innerHTML = `
                <i class="fas fa-search" style="font-size: 64px; color: var(--muted); margin-bottom: 16px;"></i>
                <h3>لم يتم العثور على نتائج</h3>
                <p>لم نجد منتجات تطابق البحث عن "${searchTerm}"</p>
                <button onclick="clearSearch()" class="btn btn-primary">مسح البحث</button>
            `;
            productsContainer.appendChild(emptyState);
        }
    }
    
    function hideEmptySearchState() {
        const emptyState = document.querySelector('.search-empty-state');
        if (emptyState) {
            emptyState.remove();
        }
    }
    
    // Add to global scope for button onclick
    window.clearSearch = function() {
        if (searchInput) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
        }
    };
});

// CSS Animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .search-empty-state {
        grid-column: 1 / -1;
        text-align: center;
        padding: 60px 20px;
    }
`;
document.head.appendChild(style);