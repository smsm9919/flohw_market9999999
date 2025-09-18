import os
import logging
import secrets
import datetime
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from i18n import i18n

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)

# Initialize i18n
i18n.init_app(app)

# Environment configurations
app.secret_key = os.environ.get("SECRET_KEY", "flohmarkt_secret_key_production_2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default

# Create uploads directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
login_manager.login_message_category = 'error'

# Import models after db initialization
from models import User, Category, Product, PriceNegotiation, Message

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    """Initialize database with tables and sample data"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Create categories if they don't exist
            categories = [
                'سيارات مستعملة', 'الهواتف المحمولة', 'الإلكترونيات', 
                'سماعات لاسلكية', 'كاميرات احترافية', 'أثاث منزلي',
                'أزياء وإكسسوارات', 'عقارات', 'فرص عمل'
            ]
            
            for cat_name in categories:
                if not Category.query.filter_by(name=cat_name).first():
                    category = Category()
                    category.name = cat_name
                    db.session.add(category)
            
            # Create admin user if doesn't exist
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@flowmarket.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            if not User.query.filter_by(email=admin_email).first():
                admin_user = User()
                admin_user.fullname = 'مدير النظام'
                admin_user.email = admin_email
                admin_user.phone = '+201000000000'
                admin_user.password = generate_password_hash(admin_password)
                admin_user.role = 'admin'
                db.session.add(admin_user)
                logger.info(f"Admin user created: {admin_email}")
            
            # Create test user if doesn't exist
            test_email = 'user@flowmarket.com'
            if not User.query.filter_by(email=test_email).first():
                test_user = User()
                test_user.fullname = 'مستخدم تجريبي'
                test_user.email = test_email
                test_user.phone = '+201007654321'
                test_user.password = generate_password_hash('user123')
                test_user.role = 'user'
                db.session.add(test_user)
                logger.info(f"Test user created: {test_email}")
            
            db.session.commit()
            logger.info("Database initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            db.session.rollback()

# ===== Helper Functions =====
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        if current_user.role != 'admin':
            flash('صفحة محظورة', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ===== Routes =====

@app.route('/')
def index():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/healthz')
def healthz():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'database': 'disconnected'
        }), 500

# Legacy health endpoint
@app.route('/health')
def health_check():
    """Legacy health check endpoint"""
    return redirect(url_for('healthz'))

# ===== API Endpoints for Admin Panel =====
@app.route('/api/debug/auth')
def api_debug_auth():
    """Debug endpoint to check authentication status"""
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'user_role': current_user.role if current_user.is_authenticated else None,
        'user_email': current_user.email if current_user.is_authenticated else None
    })

@app.route('/api/categories')
def api_categories():
    """API endpoint to get all categories"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        categories = Category.query.all()
        categories_data = []
        for cat in categories:
            categories_data.append({
                'id': cat.id,
                'name': cat.name,
                'product_count': len(cat.products)
            })
        return jsonify(categories_data)
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return jsonify({'error': 'فشل في تحميل الفئات'}), 500

@app.route('/api/admin/products')
def api_admin_products():
    """API endpoint to get all products for admin"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Show all products for admin (no approval filtering needed)
        products = Product.query.order_by(Product.created_at.desc()).all()
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'category': product.category.name if product.category else 'غير محدد',
                'seller': product.user.fullname if product.user else 'غير محدد',
                'seller_email': product.user.email if product.user else 'غير محدد',
                'status': product.status,
                'image_url': product.image_url,
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M') if product.created_at else ''
            })
        return jsonify(products_data)
    except Exception as e:
        logger.error(f"Error fetching admin products: {e}")
        return jsonify({'error': 'فشل في تحميل المنتجات'}), 500

@app.route('/api/admin/users')
def api_admin_users():
    """API endpoint to get all users for admin"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        users = User.query.all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'fullname': user.fullname,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'product_count': len(user.products),
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else ''
            })
        return jsonify(users_data)
    except Exception as e:
        logger.error(f"Error fetching admin users: {e}")
        return jsonify({'error': 'فشل في تحميل المستخدمين'}), 500

@app.route('/api/admin/product/<int:product_id>/approve', methods=['POST'])
def api_approve_product(product_id):
    """API endpoint to approve a product"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        product = Product.query.get_or_404(product_id)
        product.status = 'approved'
        db.session.commit()
        logger.info(f"Product {product_id} approved by admin {current_user.email}")
        return jsonify({'success': True, 'message': 'تم قبول المنتج بنجاح'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving product {product_id}: {e}")
        return jsonify({'error': 'فشل في قبول المنتج'}), 500

@app.route('/api/admin/product/<int:product_id>/reject', methods=['POST'])
def api_reject_product(product_id):
    """API endpoint to reject a product"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        product = Product.query.get_or_404(product_id)
        product.status = 'rejected'
        db.session.commit()
        logger.info(f"Product {product_id} rejected by admin {current_user.email}")
        return jsonify({'success': True, 'message': 'تم رفض المنتج'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting product {product_id}: {e}")
        return jsonify({'error': 'فشل في رفض المنتج'}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            fullname = request.form.get('fullname', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            # Simple validation
            if not all([fullname, email, password]):
                flash('جميع الحقول مطلوبة', 'error')
                return render_template('register.html')
            
            if len(password) < 6:
                flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
                return render_template('register.html')
            
            # Check if email exists
            if User.query.filter_by(email=email).first():
                flash('البريد الإلكتروني مسجل مسبقًا', 'error')
                return render_template('register.html')
            
            # Create new user
            user = User()
            user.fullname = fullname
            user.email = email
            user.password = generate_password_hash(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Auto-login after successful registration using Flask-Login
            login_user(user, remember=False)
            
            logger.info(f"New user registered and auto-logged in: {email}")
            flash(f'مرحباً بك {user.fullname}! تم إنشاء حسابك بنجاح', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            flash('حدث خطأ أثناء التسجيل', 'error')
            db.session.rollback()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect based on role
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            if not email or not password:
                flash('خطأ في البريد أو كلمة المرور', 'error')
                return render_template('login.html')
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                # Login user with Flask-Login (automatic session management)
                login_user(user, remember=True)  # Always remember for simplicity
                
                logger.info(f"Successful login for user {email}")
                
                # Direct redirect based on role without flash messages
                if user.role == 'admin':
                    return redirect(url_for('admin_panel'))
                else:
                    return redirect(url_for('index'))
            else:
                logger.warning(f"Failed login attempt for email: {email}")
                flash('خطأ في البريد أو كلمة المرور', 'error')
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('خطأ في البريد أو كلمة المرور', 'error')
    
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            
            if not email:
                flash('البريد الإلكتروني مطلوب', 'error')
                return render_template('forgot_password.html')
            
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Generate reset token (in production, this should be sent via email)
                reset_token = secrets.token_urlsafe(32)
                user.reset_token = reset_token
                user.reset_token_expires = datetime.now() + timedelta(hours=1)
                db.session.commit()
                
                logger.info(f"Password reset requested for user {email}")
                
                # In production, send email here
                # For demo purposes, we'll show a success message
                flash(f'تم إرسال رابط إعادة تعيين كلمة المرور إلى {email}. ' + 
                      f'للتجربة: /reset_password/{reset_token}', 'success')
            else:
                # Don't reveal if user exists or not for security
                flash(f'إذا كان البريد الإلكتروني {email} مسجل لدينا، فسنرسل لك رابط إعادة التعيين', 'success')
                
        except Exception as e:
            logger.error(f"Forgot password error: {str(e)}")
            flash('حدث خطأ. يرجى المحاولة مرة أخرى', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.now():
        flash('رابط إعادة التعيين غير صالح أو منتهي الصلاحية', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        try:
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not password or not confirm_password:
                flash('كلمة المرور وتأكيدها مطلوبان', 'error')
                return render_template('reset_password.html')
            
            if password != confirm_password:
                flash('كلمة المرور غير متطابقة', 'error')
                return render_template('reset_password.html')
            
            if len(password) < 6:
                flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
                return render_template('reset_password.html')
            
            # Update password
            user.password = generate_password_hash(password)
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()
            
            logger.info(f"Password reset completed for user {user.email}")
            flash('تم تحديث كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            logger.error(f"Reset password error: {str(e)}")
            flash('حدث خطأ أثناء تحديث كلمة المرور', 'error')
            db.session.rollback()
    
    return render_template('reset_password.html')

@app.route('/logout')
@login_required
def logout():
    user_name = current_user.fullname
    logout_user()
    flash(f'وداعاً {user_name}، تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('index'))

@app.route('/products')
def products():
    category_name = request.args.get('category')
    products = Product.query.filter_by(status='approved')
    
    if category_name:
        category = Category.query.filter_by(name=category_name).first()
        if category:
            products = products.filter_by(category_id=category.id)
    
    products = products.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    
    return render_template('products.html', products=products, categories=categories, selected_category=category_name)

@app.route('/product/<int:product_id>')
def product_details(product_id):
    # Get product with seller information
    product = db.session.query(Product, User.phone.label('seller_phone')).join(
        User, Product.user_id == User.id
    ).filter(Product.id == product_id, Product.status == 'approved').first_or_404()
    
    # Convert to dict format for template compatibility
    product_dict = {
        'id': product.Product.id,
        'name': product.Product.name,
        'description': product.Product.description,
        'price': product.Product.price,
        'image_url': product.Product.image_url,
        'category_name': product.Product.category.name if product.Product.category else '',
        'fullname': product.Product.user.fullname,
        'user_id': product.Product.user_id,
        'seller_phone': product.seller_phone,
        'created_at': product.Product.created_at
    }
    
    return render_template('product_details.html', product=product_dict)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = float(request.form.get('price', 0))
            category_id = int(request.form.get('category_id', 0))
            
            if not all([name, price, category_id]):
                flash('اسم المنتج والسعر والفئة مطلوبة', 'error')
                return redirect(url_for('add_product'))
            
            # Handle image upload
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_url = f"/static/uploads/{filename}"
            
            # Create product
            product = Product()
            product.name = name
            product.description = description
            product.price = price
            product.category_id = category_id
            product.image_url = image_url
            product.user_id = current_user.id
            # Auto-approve all products immediately - no approval workflow
            product.status = 'approved'
            flash('تم إضافة المنتج بنجاح وتم نشره فوراً في المتجر', 'success')
            
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('my_products'))
            
        except Exception as e:
            logger.error(f"Add product error: {str(e)}")
            flash('حدث خطأ أثناء إضافة المنتج', 'error')
            db.session.rollback()
    
    categories = Category.query.all()
    return render_template('add_product.html', categories=categories)

@app.route('/my_products')
@login_required
def my_products():
    products = Product.query.filter_by(user_id=current_user.id).order_by(Product.created_at.desc()).all()
    return render_template('my_products.html', products=products)

@app.route('/seller_inbox')
@login_required
def seller_inbox():
    """Display seller's message inbox with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if current_user.role == 'admin':
        # Admin can see all messages
        messages_query = Message.query.join(Product).order_by(Message.created_at.desc())
    else:
        # Regular sellers see only messages for their products
        messages_query = Message.query.join(Product).filter(
            Product.user_id == current_user.id
        ).order_by(Message.created_at.desc())
    
    pagination = messages_query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    messages = pagination.items
    
    return render_template('seller_inbox.html', messages=messages, pagination=pagination)

@app.route('/store')
def store():
    """Alternative route to products page for compatibility"""
    return redirect(url_for('products'))

@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_product(product_id):
    """Delete a product - admin can delete any, users can delete their own"""
    product = Product.query.get_or_404(product_id)
    
    # Only admin can delete products
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية لحذف المنتجات', 'error')
        return redirect(url_for('my_products'))
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('تم حذف المنتج بنجاح', 'success')
        logger.info(f"Product {product_id} deleted by user {current_user.email}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting product {product_id}: {e}")
        flash('حدث خطأ أثناء حذف المنتج', 'error')
    
    if current_user.role == 'admin':
        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('my_products'))

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit a product - admin can edit any, users can edit their own"""
    product = Product.query.get_or_404(product_id)
    
    # Only admin can edit products
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية لتعديل المنتجات', 'error')
        return redirect(url_for('my_products'))
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name', '').strip()
            product.description = request.form.get('description', '').strip()
            product.price = float(request.form.get('price', 0))
            product.category_id = int(request.form.get('category_id', 0))
            
            # Handle image upload if provided
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    product.image_url = f"/static/uploads/{filename}"
            
            # Admin can change status
            if current_user.role == 'admin':
                status = request.form.get('status', product.status)
                if status in ['pending', 'approved', 'rejected']:
                    product.status = status
            
            db.session.commit()
            flash('تم تحديث المنتج بنجاح', 'success')
            logger.info(f"Product {product_id} updated by user {current_user.email}")
            
            if current_user.role == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('my_products'))
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating product {product_id}: {e}")
            flash('حدث خطأ أثناء تحديث المنتج', 'error')
    
    categories = Category.query.all()
    return render_template('edit_product.html', product=product, categories=categories)



@app.route('/jobs')
def jobs():
    category = Category.query.filter_by(name='فرص عمل').first()
    jobs = []
    if category:
        jobs = Product.query.filter_by(category_id=category.id, status='approved').order_by(Product.created_at.desc()).all()
    
    return render_template('jobs.html', jobs=jobs)

# ===== Admin Routes =====

@app.route('/admin')
@app.route('/admin_panel')
@admin_required
def admin_panel():
    # Statistics
    total_users = User.query.count()
    total_products = Product.query.count()
    pending_products = Product.query.filter_by(status='pending').count()
    approved_products = Product.query.filter_by(status='approved').count()
    total_messages = Message.query.count()
    unread_messages = Message.query.filter_by(is_read=False).count()
    
    # Recent products for approval
    pending_products_list = Product.query.filter_by(status='pending').order_by(Product.created_at.desc()).limit(10).all()
    
    # Recent messages for review
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'total_products': total_products,
        'pending_products': pending_products,
        'approved_products': approved_products,
        'total_messages': total_messages,
        'unread_messages': unread_messages
    }
    
    return render_template('admin_panel.html', stats=stats, pending_products=pending_products_list, recent_messages=recent_messages)

@app.route('/admin/approve_product/<int:product_id>', methods=['POST'])
@admin_required
def approve_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        product.status = 'approved'
        db.session.commit()
        
        flash(f'تمت الموافقة على المنتج: {product.name}', 'success')
        
    except Exception as e:
        logger.error(f"Approve product error: {str(e)}")
        flash('حدث خطأ أثناء الموافقة على المنتج', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/reject_product/<int:product_id>', methods=['POST'])
@admin_required
def reject_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        product.status = 'rejected'
        db.session.commit()
        
        flash(f'تم رفض المنتج: {product.name}', 'success')
        
    except Exception as e:
        logger.error(f"Reject product error: {str(e)}")
        flash('حدث خطأ أثناء رفض المنتج', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_product_admin/<int:product_id>', methods=['POST'])
@admin_required
def delete_product_admin(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        # Delete image file if exists
        if product.image_url and product.image_url.startswith('/static/uploads/'):
            try:
                image_path = product.image_url[1:]  # Remove leading slash
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                logger.warning(f"Failed to delete image file: {str(e)}")
        
        product_name = product.name
        db.session.delete(product)
        db.session.commit()
        
        flash(f'تم حذف المنتج: {product_name}', 'success')
        
    except Exception as e:
        logger.error(f"Admin delete product error: {str(e)}")
        flash('حدث خطأ أثناء حذف المنتج', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_panel'))

# ===== Price Negotiation Routes =====

@app.route('/api/negotiate_price', methods=['POST'])
@login_required
def negotiate_price():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        offered_price = float(data.get('offered_price'))
        message = data.get('message', '')
        
        # Get product
        product = Product.query.get_or_404(product_id)
        
        # Check if user is not the owner
        if product.user_id == current_user.id:
            return jsonify({'success': False, 'message': 'لا يمكنك التفاوض على سعر منتجك الخاص'})
        
        # Check if there's already a pending negotiation from this user
        existing_negotiation = PriceNegotiation.query.filter_by(
            product_id=product_id,
            buyer_id=current_user.id,
            status='pending'
        ).first()
        
        if existing_negotiation:
            # Update existing negotiation
            existing_negotiation.offered_price = offered_price
            existing_negotiation.message = message
            existing_negotiation.updated_at = datetime.utcnow()
        else:
            # Create new negotiation
            negotiation = PriceNegotiation()
            negotiation.product_id = product_id
            negotiation.buyer_id = current_user.id
            negotiation.offered_price = offered_price
            negotiation.message = message
            db.session.add(negotiation)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '✅ تم إرسال عرضك إلى البائع بنجاح!',
            'offered_price': offered_price
        })
        
    except Exception as e:
        logger.error(f"Price negotiation error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إرسال العرض'})

@app.route('/api/contact_seller', methods=['POST'])
def contact_seller():
    """Send message to seller - no login required"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        seller_id = data.get('seller_id')
        buyer_name = data.get('buyer_name', '').strip()
        buyer_email = data.get('buyer_email', '').strip()
        message_text = data.get('message_text', '').strip()
        
        # Validation
        if not all([product_id, seller_id, buyer_name, buyer_email, message_text]):
            return jsonify({'success': False, 'message': 'يرجى ملء جميع الحقول المطلوبة'})
        
        # Email validation
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, buyer_email):
            return jsonify({'success': False, 'message': 'يرجى إدخال بريد إلكتروني صحيح'})
        
        # Get product and seller
        product = Product.query.get_or_404(product_id)
        seller = User.query.get_or_404(seller_id)
        
        # Check if seller is available (optional feature)
        if not seller:
            return jsonify({'success': False, 'message': 'البائع غير متاح حاليًا، سيتم التواصل معك لاحقًا'})
        
        # Create message record
        message = Message()
        message.product_id = product_id
        message.seller_id = seller_id
        message.buyer_name = buyer_name
        message.buyer_email = buyer_email
        message.message_text = message_text
        message.is_read = False
        
        db.session.add(message)
        db.session.commit()
        
        # Log the message
        logger.info(f"New message from {buyer_email} to seller {seller.email} for product {product.name}")
        
        # Send real email notification to seller
        try:
            email_subject = f"رسالة جديدة بخصوص منتجك: {product.name}"
            email_content = f"""
مرحباً {seller.fullname},

لديك رسالة جديدة بخصوص منتجك: {product.name}

من: {buyer_name}
البريد الإلكتروني: {buyer_email}
الرسالة: {message_text}

يرجى التواصل مع المشتري على البريد الإلكتروني المذكور أعلاه.

تحياتي،
فريق فلوماركت
            """
            
            success = send_email_notification(seller.email, email_subject, email_content)
            if success:
                logger.info(f"✅ EMAIL DELIVERY CONFIRMED - Message sent to seller: {seller.email}")
                # Update message record to mark as email sent
                message.email_sent = True
                message.email_sent_at = datetime.utcnow()
                db.session.commit()
            else:
                logger.error(f"❌ EMAIL DELIVERY FAILED - Could not send to: {seller.email}")
                message.email_sent = False
                db.session.commit()
            
        except Exception as email_error:
            logger.warning(f"Failed to send email notification: {str(email_error)}")
            # Don't fail the whole process if email fails
        
        return jsonify({
            'success': True,
            'message': '✅ تم إرسال رسالتك إلى البائع بنجاح!'
        })
        
    except Exception as e:
        logger.error(f"Contact seller error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إرسال الرسالة. يرجى المحاولة مرة أخرى.'})

@app.route('/api/seller_reply', methods=['POST'])
@login_required
def seller_reply():
    """Send reply from seller to buyer"""
    try:
        data = request.get_json()
        logger.info(f"Seller reply request data: {data}")
        
        message_id = data.get('message_id')
        to_email = data.get('to_email', '').strip()
        subject = data.get('subject', '').strip()
        message_text = data.get('message', '').strip()
        
        # Validation with detailed error logging
        if not message_id:
            logger.error("Missing message_id in reply request")
            return jsonify({'success': False, 'message': 'معرف الرسالة مطلوب'})
        
        if not to_email:
            logger.error("Missing to_email in reply request")
            return jsonify({'success': False, 'message': 'البريد الإلكتروني مطلوب'})
        
        if not subject:
            logger.error("Missing subject in reply request")
            return jsonify({'success': False, 'message': 'موضوع الرسالة مطلوب'})
        
        if not message_text:
            logger.error("Missing message_text in reply request")
            return jsonify({'success': False, 'message': 'نص الرسالة مطلوب'})
        
        # Email validation
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, to_email):
            logger.error(f"Invalid email format: {to_email}")
            return jsonify({'success': False, 'message': 'يرجى إدخال بريد إلكتروني صحيح'})
        
        # Get original message and verify ownership
        try:
            original_message = Message.query.get(message_id)
            if not original_message:
                logger.error(f"Message not found: {message_id}")
                return jsonify({'success': False, 'message': 'الرسالة غير موجودة'})
            
            product = Product.query.get(original_message.product_id)
            if not product:
                logger.error(f"Product not found: {original_message.product_id}")
                return jsonify({'success': False, 'message': 'المنتج غير موجود'})
        
        except Exception as db_error:
            logger.error(f"Database error in seller_reply: {str(db_error)}")
            return jsonify({'success': False, 'message': 'خطأ في قاعدة البيانات'})
        
        # Check if current user is the seller (product owner) or admin
        if current_user.role != 'admin' and product.user_id != current_user.id:
            logger.error(f"Unauthorized reply attempt by user {current_user.id} for product {product.id}")
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية للرد على هذه الرسالة'})
        
        # Create the reply entry for thread tracking
        reply_record = Message()
        reply_record.product_id = product.id
        reply_record.seller_id = current_user.id
        reply_record.buyer_name = f"رد من {current_user.fullname}"
        reply_record.buyer_email = current_user.email
        reply_record.message_text = message_text
        reply_record.is_read = True
        reply_record.is_reply = True  # Mark as seller reply
        reply_record.parent_message_id = message_id
        
        # Send email reply
        email_content = f"""
مرحباً {original_message.buyer_name},

{message_text}

هذا رد من البائع {current_user.fullname} بخصوص منتج: {product.name}

للتواصل المباشر:
البريد الإلكتروني: {current_user.email}
{f"الهاتف: {current_user.phone}" if hasattr(current_user, 'phone') and current_user.phone else ""}

تحياتي،
{current_user.fullname}
فلوماركت
        """
        
        # Try to send email, but don't fail if email service is down
        email_success = False
        try:
            email_success = send_email_notification(to_email, subject, email_content)
            logger.info(f"Email send attempt result: {email_success}")
        except Exception as email_error:
            logger.warning(f"Email sending failed, but continuing with reply: {str(email_error)}")
        
        # Save the reply record regardless of email status
        try:
            db.session.add(reply_record)
            # Mark original message as read
            original_message.is_read = True
            db.session.commit()
            logger.info(f"✅ REPLY SAVED - From seller {current_user.email} to buyer {to_email}")
            
            response_message = '✅ تم إرسال الرد بنجاح!'
            if not email_success:
                response_message += ' (تم حفظ الرد، ولكن قد يكون هناك تأخير في إرسال البريد الإلكتروني)'
            
            return jsonify({
                'success': True, 
                'message': response_message,
                'email_sent': email_success
            })
            
        except Exception as save_error:
            logger.error(f"Failed to save reply: {str(save_error)}")
            db.session.rollback()
            return jsonify({'success': False, 'message': 'فشل في حفظ الرد'})
        
    except Exception as e:
        logger.error(f"Seller reply error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ غير متوقع: {str(e)}'})

@app.route('/api/mark_message_read', methods=['POST'])
@login_required
def mark_message_read():
    """Mark message as read or unread"""
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        mark_as_read = data.get('mark_as_read', True)
        
        if not message_id:
            return jsonify({'success': False, 'message': 'معرف الرسالة مطلوب'})
        
        message = Message.query.get_or_404(message_id)
        product = Product.query.get_or_404(message.product_id)
        
        # Check if current user is the seller (product owner) or admin
        if current_user.role != 'admin' and product.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لتعديل هذه الرسالة'})
        
        message.is_read = mark_as_read
        db.session.commit()
        
        status_text = 'مقروءة' if mark_as_read else 'غير مقروءة'
        return jsonify({'success': True, 'message': f'تم تحديث حالة الرسالة إلى {status_text}'})
        
    except Exception as e:
        logger.error(f"Mark message read error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء تحديث الرسالة'})

@app.route('/api/unread_messages_count')
@login_required
def unread_messages_count():
    """Get count of unread messages for current user"""
    try:
        if current_user.role == 'admin':
            # Admin can see all unread messages
            count = Message.query.filter_by(is_read=False).count()
        else:
            # Regular users see unread messages for their products
            count = Message.query.join(Product).filter(
                Product.user_id == current_user.id,
                Message.is_read == False
            ).count()
        
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        logger.error(f"Unread messages count error: {str(e)}")
        return jsonify({'success': False, 'count': 0})

@app.route('/api/message_thread/<int:message_id>')
@login_required
def message_thread(message_id):
    """Get message thread with replies"""
    try:
        # Get original message
        original_message = Message.query.get_or_404(message_id)
        product = Product.query.get_or_404(original_message.product_id)
        
        # Check if current user is the seller (product owner) or admin
        if current_user.role != 'admin' and product.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'ليس لديك صلاحية لعرض هذه الرسالة'})
        
        # Get all replies for this message
        replies = Message.query.filter_by(parent_message_id=message_id).order_by(Message.created_at.asc()).all()
        
        replies_data = []
        for reply in replies:
            replies_data.append({
                'id': reply.id,
                'message': reply.message_text,
                'sender_type': 'seller' if reply.is_reply else 'buyer',
                'sender_name': reply.buyer_name,
                'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return jsonify({
            'success': True,
            'replies': replies_data,
            'original_message': {
                'id': original_message.id,
                'message': original_message.message_text,
                'buyer_name': original_message.buyer_name,
                'created_at': original_message.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except Exception as e:
        logger.error(f"Message thread error: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء جلب المحادثة'})

def send_email_notification(to_email, subject, content):
    """Send real email notification using SendGrid"""
    try:
        import os
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        # Check if SendGrid API key is available
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_key:
            logger.warning("SendGrid API key not found - email sending disabled")
            logger.info(f"Email content for {to_email}: {content}")
            return False
        
        # Create email message with proper formatting
        html_content = f"""
        <div style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
            <h2 style="color: #2c5aa0;">رسالة جديدة من فلوماركت</h2>
            {content.replace(chr(10), '<br>')}
            <hr style="margin: 20px 0;">
            <p style="color: #666; font-size: 14px;">
                هذه رسالة تلقائية من موقع فلوماركت. يرجى عدم الرد على هذا البريد الإلكتروني.
            </p>
        </div>
        """
        
        message = Mail(
            from_email='noreply@flowmarket.com',
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        # Send email with detailed logging
        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)
        
        # Log detailed response information
        logger.info(f"SendGrid Response Status: {response.status_code}")
        logger.info(f"SendGrid Response Headers: {dict(response.headers)}")
        
        if response.status_code == 202:
            logger.info(f"✅ Message Sent Successfully to: {to_email}")
            logger.info(f"Email Subject: {subject}")
            return True
        else:
            logger.error(f"❌ Failed to Send - SendGrid error: {response.status_code}")
            logger.error(f"Response body: {response.body}")
            logger.error(f"Response headers: {dict(response.headers)}")
            return False
        
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        # Always log the email content for debugging
        logger.info(f"Email content for {to_email}:{content}")
        return False

@app.route('/api/respond_negotiation', methods=['POST'])
@login_required
def respond_negotiation():
    try:
        data = request.get_json()
        negotiation_id = data.get('negotiation_id')
        action = data.get('action')  # 'accept', 'reject', 'counter'
        counter_offer = data.get('counter_offer')
        counter_message = data.get('counter_message', '')
        
        # Get negotiation
        negotiation = PriceNegotiation.query.get_or_404(negotiation_id)
        
        # Check if user is the product owner
        if negotiation.product.user_id != session['user_id']:
            return jsonify({'success': False, 'message': 'غير مخول لك الرد على هذا العرض'})
        
        if action == 'accept':
            negotiation.status = 'accepted'
            # Optionally update product price
            # negotiation.product.price = negotiation.offered_price
        elif action == 'reject':
            negotiation.status = 'rejected'
        elif action == 'counter':
            negotiation.status = 'countered'
            negotiation.counter_offer = float(counter_offer)
            negotiation.counter_message = counter_message
        
        negotiation.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'تم {action} العرض بنجاح'
        })
        
    except Exception as e:
        logger.error(f"Negotiation response error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء الرد على العرض'})

@app.route('/api/product/<int:product_id>/negotiations')
@login_required
def get_product_negotiations(product_id):
    try:
        # Get product
        product = Product.query.get_or_404(product_id)
        
        # Check if user is the product owner
        if product.user_id != session['user_id']:
            return jsonify({'success': False, 'message': 'غير مخول لك عرض هذه البيانات'})
        
        # Get negotiations
        negotiations = PriceNegotiation.query.filter_by(product_id=product_id).order_by(PriceNegotiation.created_at.desc()).all()
        
        negotiations_data = []
        for neg in negotiations:
            negotiations_data.append({
                'id': neg.id,
                'buyer_name': neg.buyer.fullname,
                'offered_price': neg.offered_price,
                'message': neg.message,
                'status': neg.status,
                'counter_offer': neg.counter_offer,
                'counter_message': neg.counter_message,
                'created_at': neg.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return jsonify({
            'success': True,
            'negotiations': negotiations_data
        })
        
    except Exception as e:
        logger.error(f"Get negotiations error: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء جلب البيانات'})

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/products')
@admin_required
def admin_products():
    status_filter = request.args.get('status', 'all')
    products = Product.query
    
    if status_filter != 'all':
        products = products.filter_by(status=status_filter)
    
    products = products.order_by(Product.created_at.desc()).all()
    return render_template('admin_products.html', products=products, status_filter=status_filter)

# ===== Health Check Routes =====

@app.route('/healthz')
def health_check_production():
    """Health check endpoint for production monitoring"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'error: {str(e)}'
        
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'database': db_status,
        'service': 'flohmarkt-production',
        'domain': 'flowmarket.com'
    }), 200 if db_status == 'healthy' else 503

# ===== Error Handlers =====

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

@app.errorhandler(413)
def too_large(e):
    flash('حجم الملف كبير جداً. الحد الأقصى 16 ميجابايت', 'error')
    return redirect(request.url)

# SEO Routes
@app.route('/robots.txt')
def robots_txt():
    import os
    from flask import Response
    robots_content = """User-agent: *
Allow: /

# Important pages
Allow: /products
Allow: /login
Allow: /register

# Block admin areas
Disallow: /admin
Disallow: /admin/*

# Block user-specific pages
Disallow: /my_products
Disallow: /add_product

# Block API endpoints
Disallow: /api/
Disallow: /logout

# Static files
Allow: /static/

# Sitemap
Sitemap: https://flowmarket.com/sitemap.xml

# Crawl-delay
Crawl-delay: 1"""
    return Response(robots_content, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    from xml.etree.ElementTree import Element, SubElement, tostring
    from urllib.parse import quote
    
    # Create root element
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Get base URL
    base_url = request.url_root.rstrip('/')
    
    # Homepage
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = base_url + '/'
    SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    SubElement(url, 'changefreq').text = 'daily'
    SubElement(url, 'priority').text = '1.0'
    
    # Products page
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = base_url + '/products'
    SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    SubElement(url, 'changefreq').text = 'daily'
    SubElement(url, 'priority').text = '0.9'
    
    # Jobs page
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = base_url + '/jobs'
    SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    SubElement(url, 'changefreq').text = 'daily'
    SubElement(url, 'priority').text = '0.8'
    
    # Cars page
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = base_url + '/cars'
    SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    SubElement(url, 'changefreq').text = 'daily'
    SubElement(url, 'priority').text = '0.8'
    
    # Category pages
    categories = ['سيارات مستعملة', 'هواتف ذكية', 'إلكترونيات', 'سماعات لاسلكية', 
                  'كاميرات احترافية', 'أثاث منزلي', 'أزياء وإكسسوارات', 'فرص عمل']
    
    for category in categories:
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = base_url + '/products?category=' + quote(category)
        SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        SubElement(url, 'changefreq').text = 'weekly'
        SubElement(url, 'priority').text = '0.7'
    
    # Product detail pages
    products = Product.query.filter_by(status='approved').all()
    for product in products:
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = base_url + f'/product/{product.id}'
        # Use created_at since updated_at doesn't exist in Product model
        if hasattr(product, 'created_at') and product.created_at:
            SubElement(url, 'lastmod').text = product.created_at.strftime('%Y-%m-%d')
        else:
            SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        SubElement(url, 'changefreq').text = 'weekly'
        SubElement(url, 'priority').text = '0.6'
    
    # Convert to string and return as XML
    xml_str = tostring(urlset, encoding='utf-8', method='xml')
    response = app.response_class(xml_str, mimetype='application/xml')
    return response

# ===== Language Switch Route =====

@app.route('/set_language/<language>')
def set_language(language):
    """Set the current language and redirect back to referrer"""
    if i18n.set_language(language):
        flash('Language updated successfully', 'success')
    else:
        flash('Invalid language selection', 'error')
    
    # Redirect back to the previous page or home
    referrer = request.referrer
    if referrer and referrer.startswith(request.host_url):
        return redirect(referrer)
    return redirect(url_for('index'))

# Initialize database when app starts
with app.app_context():
    init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)