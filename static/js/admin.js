// Admin Panel JavaScript
class AdminPanel {
    constructor() {
        this.currentSection = 'dashboard';
        this.products = [];
        this.categories = [];
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadCategories();
        this.showSection('dashboard');
    }

    setupNavigation() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                if (section) {
                    this.showSection(section);
                    this.setActiveNavLink(link);
                }
            });
        });
    }

    setActiveNavLink(activeLink) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        activeLink.classList.add('active');
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.admin-section').forEach(section => {
            section.classList.add('hidden');
        });

        // Show selected section
        const section = document.getElementById(`${sectionName}-section`);
        if (section) {
            section.classList.remove('hidden');
            this.currentSection = sectionName;

            // Load data for the section
            switch (sectionName) {
                case 'products':
                    this.loadProducts();
                    break;
                case 'users':
                    this.loadUsers();
                    break;
                case 'categories':
                    this.loadCategoriesTable();
                    break;
            }
        }
    }

    async loadProducts() {
        const loading = document.getElementById('products-loading');
        const tableBody = document.getElementById('products-table-body');

        loading.style.display = 'block';
        tableBody.innerHTML = '';

        try {
            const response = await fetch('/api/admin/products');
            if (!response.ok) throw new Error('فشل في تحميل المنتجات');

            const products = await response.json();
            this.products = products;

            tableBody.innerHTML = products.map(product => `
                <tr>
                    <td>${product.id}</td>
                    <td>
                        ${product.image_url ? 
                            `<img src="${product.image_url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" alt="${product.name}">` : 
                            '<span style="color: var(--muted);">لا توجد صورة</span>'
                        }
                    </td>
                    <td>${product.name}</td>
                    <td>${product.category_name}</td>
                    <td>${this.formatPrice(product.price)} جنيه</td>
                    <td>${product.seller_name}</td>
                    <td>
                        <span class="status-badge status-${product.status}">
                            ${product.status === 'approved' ? 'معتمد' : 
                              product.status === 'pending' ? 'في الانتظار' : 'مرفوض'}
                        </span>
                    </td>
                    <td>
                        <div class="action-buttons">
                            ${product.status === 'pending' ? `
                            <button class="btn btn-sm btn-approve" onclick="adminPanel.approveProduct(${product.id})">
                                <i class="fas fa-check"></i>
                            </button>
                            <button class="btn btn-sm btn-reject" onclick="adminPanel.rejectProduct(${product.id})">
                                <i class="fas fa-times"></i>
                            </button>
                            ` : ''}
                            <button class="btn btn-sm btn-edit" onclick="adminPanel.editProduct(${product.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-delete" onclick="adminPanel.deleteProduct(${product.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');

        } catch (error) {
            this.showAlert('حدث خطأ في تحميل المنتجات: ' + error.message, 'error');
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--red);">فشل في تحميل البيانات</td></tr>';
        } finally {
            loading.style.display = 'none';
        }
    }

    async loadUsers() {
        const tableBody = document.getElementById('users-table-body');
        tableBody.innerHTML = '<tr><td colspan="6" class="loading">جاري التحميل...</td></tr>';

        try {
            const response = await fetch('/api/admin/users');
            if (!response.ok) throw new Error('فشل في تحميل المستخدمين');

            const users = await response.json();

            tableBody.innerHTML = users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.fullname}</td>
                    <td>${user.email}</td>
                    <td>${user.phone || 'غير محدد'}</td>
                    <td>
                        <span class="badge ${user.role === 'admin' ? 'badge-admin' : ''}" style="padding: 4px 8px; border-radius: 4px; font-size: 0.8rem;">
                            ${user.role === 'admin' ? 'مدير' : 'مستخدم'}
                        </span>
                    </td>
                    <td>${this.formatDate(user.created_at)}</td>
                </tr>
            `).join('');

        } catch (error) {
            this.showAlert('حدث خطأ في تحميل المستخدمين: ' + error.message, 'error');
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--red);">فشل في تحميل البيانات</td></tr>';
        }
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            if (!response.ok) throw new Error('فشل في تحميل الفئات');

            this.categories = await response.json();
            this.updateCategorySelect();

        } catch (error) {
            console.error('خطأ في تحميل الفئات:', error);
        }
    }

    async loadCategoriesTable() {
        const tableBody = document.getElementById('categories-table-body');
        tableBody.innerHTML = '<tr><td colspan="4" class="loading">جاري التحميل...</td></tr>';

        try {
            await this.loadCategories();
            
            // Get product counts for each category
            const response = await fetch('/api/admin/products');
            const products = await response.json();
            
            const categoryCounts = {};
            products.forEach(product => {
                categoryCounts[product.category_name] = (categoryCounts[product.category_name] || 0) + 1;
            });

            tableBody.innerHTML = this.categories.map(category => `
                <tr>
                    <td>${category.id}</td>
                    <td>${category.name}</td>
                    <td>${categoryCounts[category.name] || 0}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn btn-sm btn-edit" onclick="adminPanel.editCategory(${category.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-delete" onclick="adminPanel.deleteCategory(${category.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');

        } catch (error) {
            this.showAlert('حدث خطأ في تحميل الفئات: ' + error.message, 'error');
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--red);">فشل في تحميل البيانات</td></tr>';
        }
    }

    updateCategorySelect() {
        const select = document.getElementById('product-category');
        select.innerHTML = '<option value="">اختر الفئة</option>' +
            this.categories.map(cat => `<option value="${cat.id}">${cat.name}</option>`).join('');
    }

    editProduct(productId) {
        const product = this.products.find(p => p.id === productId);
        if (!product) return;

        document.getElementById('product-modal-title').textContent = 'تعديل المنتج';
        document.getElementById('product-id').value = product.id;
        document.getElementById('product-name').value = product.name;
        document.getElementById('product-description').value = product.description || '';
        document.getElementById('product-price').value = product.price;
        document.getElementById('product-image').value = product.image_url || '';
        
        // Set category
        const categorySelect = document.getElementById('product-category');
        const category = this.categories.find(c => c.name === product.category_name);
        if (category) {
            categorySelect.value = category.id;
        }

        document.getElementById('product-modal').classList.add('show');
    }

    async deleteProduct(productId) {
        if (!confirm('هل أنت متأكد من حذف هذا المنتج؟')) return;

        try {
            const response = await fetch(`/api/admin/products/${productId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('فشل في حذف المنتج');

            this.showAlert('تم حذف المنتج بنجاح', 'success');
            this.loadProducts();

        } catch (error) {
            this.showAlert('حدث خطأ في حذف المنتج: ' + error.message, 'error');
        }
    }

    async approveProduct(productId) {
        try {
            const response = await fetch(`/api/admin/products/${productId}/approve`, {
                method: 'POST'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'فشل في الموافقة على المنتج');
            }

            const result = await response.json();
            this.showAlert(result.message || 'تم قبول المنتج بنجاح', 'success');
            this.loadProducts();

        } catch (error) {
            this.showAlert('حدث خطأ: ' + error.message, 'error');
        }
    }

    async rejectProduct(productId) {
        if (!confirm('هل أنت متأكد من رفض هذا المنتج؟')) return;

        try {
            const response = await fetch(`/api/admin/products/${productId}/reject`, {
                method: 'POST'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'فشل في رفض المنتج');
            }

            const result = await response.json();
            this.showAlert(result.message || 'تم رفض المنتج', 'success');
            this.loadProducts();

        } catch (error) {
            this.showAlert('حدث خطأ: ' + error.message, 'error');
        }
    }

    formatPrice(price) {
        return new Intl.NumberFormat('ar-EG').format(price);
    }

    formatDate(dateString) {
        if (!dateString) return 'غير محدد';
        const date = new Date(dateString);
        return date.toLocaleDateString('ar-EG');
    }

    async addCategory(categoryName) {
        try {
            const response = await fetch('/api/admin/categories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: categoryName })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'حدث خطأ في الخادم');
            }

            this.showAlert('تم إضافة الفئة بنجاح', 'success');
            this.loadCategories();
            this.loadCategoriesTable();

        } catch (error) {
            this.showAlert('حدث خطأ: ' + error.message, 'error');
        }
    }

    async editCategory(categoryId) {
        const category = this.categories.find(c => c.id === categoryId);
        if (!category) return;

        const newName = prompt('ادخل الاسم الجديد للفئة:', category.name);
        if (!newName || !newName.trim() || newName.trim() === category.name) return;

        try {
            const response = await fetch(`/api/admin/categories/${categoryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: newName.trim() })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'حدث خطأ في الخادم');
            }

            this.showAlert('تم تحديث الفئة بنجاح', 'success');
            this.loadCategories();
            this.loadCategoriesTable();

        } catch (error) {
            this.showAlert('حدث خطأ: ' + error.message, 'error');
        }
    }

    async deleteCategory(categoryId) {
        if (!confirm('هل أنت متأكد من حذف هذه الفئة؟')) return;

        try {
            const response = await fetch(`/api/admin/categories/${categoryId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'حدث خطأ في الخادم');
            }

            this.showAlert('تم حذف الفئة بنجاح', 'success');
            this.loadCategories();
            this.loadCategoriesTable();

        } catch (error) {
            this.showAlert('حدث خطأ: ' + error.message, 'error');
        }
    }

    showAlert(message, type = 'success') {
        const alertsContainer = document.getElementById('alerts');
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;

        alertsContainer.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Modal functions
function openAddProductModal() {
    document.getElementById('product-modal-title').textContent = 'إضافة منتج جديد';
    document.getElementById('product-form').reset();
    document.getElementById('product-id').value = '';
    document.getElementById('product-modal').classList.add('show');
}

function closeProductModal() {
    document.getElementById('product-modal').classList.remove('show');
}

function openAddCategoryModal() {
    const categoryName = prompt('ادخل اسم الفئة الجديدة:');
    if (!categoryName || !categoryName.trim()) return;
    
    adminPanel.addCategory(categoryName.trim());
}

// Form submission
document.getElementById('product-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const productId = document.getElementById('product-id').value;
    const formData = {
        name: document.getElementById('product-name').value,
        description: document.getElementById('product-description').value,
        price: parseFloat(document.getElementById('product-price').value),
        category_id: parseInt(document.getElementById('product-category').value),
        image_url: document.getElementById('product-image').value
    };

    try {
        let response;
        
        if (productId) {
            // Update existing product
            response = await fetch(`/api/admin/products/${productId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
        } else {
            // Create new product
            response = await fetch('/api/products', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'حدث خطأ في الخادم');
        }

        adminPanel.showAlert(productId ? 'تم تحديث المنتج بنجاح' : 'تم إضافة المنتج بنجاح', 'success');
        closeProductModal();
        adminPanel.loadProducts();

    } catch (error) {
        adminPanel.showAlert('حدث خطأ: ' + error.message, 'error');
    }
});

// Initialize admin panel
const adminPanel = new AdminPanel();// Admin Panel Approval Functions

async function approveProduct(id) {
    try {
        const response = await fetch(`/api/admin/products/${id}/approve`, {
            method: 'POST'
        });
        
        if (response.ok) {
            location.reload(); // Refresh page
            alert('تم قبول المنتج بنجاح');
        } else {
            throw new Error('فشل في قبول المنتج');
        }
    } catch (error) {
        alert('حدث خطأ في قبول المنتج');
    }
}

async function rejectProduct(id) {
    if (!confirm('هل أنت متأكد من رفض هذا المنتج؟')) return;
    
    try {
        const response = await fetch(`/api/admin/products/${id}/reject`, {
            method: 'POST'
        });
        
        if (response.ok) {
            location.reload(); // Refresh page
            alert('تم رفض المنتج');
        } else {
            throw new Error('فشل في رفض المنتج');
        }
    } catch (error) {
        alert('حدث خطأ في رفض المنتج');
    }
}
