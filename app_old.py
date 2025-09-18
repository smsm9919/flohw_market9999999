import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your_secret_key_here")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app, model_class=Base)

# ===== Models =====
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    products = db.relationship('Product', backref='seller', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def init_db():
    with app.app_context():
        db.create_all()
        
        # Seed categories
        if Category.query.count() == 0:
            categories = [
                'سيارات مستعملة', 'إلكترونيات', 'أثاث منزلي', 
                'ملابس وإكسسوارات', 'فرص عمل', 'هواتف محمولة',
                'سماعات لاسلكية', 'كاميرات احترافية'
            ]
            for cat_name in categories:
                category = Category(name=cat_name)
                db.session.add(category)
            db.session.commit()
        
        # Seed admin user
        admin_user = User.query.filter_by(email='admin@flohmarkt.com').first()
        if not admin_user:
            admin = User(
                fullname='مدير النظام',
                email='admin@flohmarkt.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
        
        # Seed sample user
        sample_user = User.query.filter_by(email='user@example.com').first()
        if not sample_user:
            user = User(
                fullname='مستخدم تجريبي',
                email='user@example.com',
                phone='0123456789',
                password=generate_password_hash('password123')
            )
            db.session.add(user)
            db.session.commit()
            
        # Seed sample products
        if Product.query.count() == 0:
            electronics = Category.query.filter_by(name='إلكترونيات').first()
            cars = Category.query.filter_by(name='سيارات مستعملة').first()
            jobs = Category.query.filter_by(name='فرص عمل').first()
            furniture = Category.query.filter_by(name='أثاث منزلي').first()
            fashion = Category.query.filter_by(name='ملابس وإكسسوارات').first()
            phones = Category.query.filter_by(name='هواتف محمولة').first()
            headphones = Category.query.filter_by(name='سماعات لاسلكية').first()
            cameras = Category.query.filter_by(name='كاميرات احترافية').first()
            user = User.query.filter_by(email='user@example.com').first()
            
            products = [
                # Electronics
                Product(
                    name='ساعة ذكية - Apple Watch Series 9',
                    description='ساعة ذكية بحالة ممتازة، شاشة بحالة ممتازة، جميع الميزات تعمل بشكل ممتاز مع نظام watchOS الأحدث',
                    price=5330,
                    category_id=electronics.id,
                    image_url='https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id,
                    status='approved'
                ),
                
                # Cars
                Product(
                    name='مرسيدس بنز C200 موديل 2020',
                    description='سيارة مرسيدس بنز فخمة، حالة ممتازة، فل كامل، صيانة دورية، بدون حوادث، 25,000 كم فقط',
                    price=950000,
                    category_id=cars.id,
                    image_url='https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                # Mobile Phones  
                Product(
                    name='iPhone 15 Pro - 256GB',
                    description='هاتف iPhone 15 Pro بذاكرة 256GB، حالة ممتازة، مع العلبة الأصلية وجميع الملحقات',
                    price=45000,
                    category_id=phones.id,
                    image_url='https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                Product(
                    name='Samsung Galaxy S24 Ultra',
                    description='هاتف سامسونغ الرائد مع قلم S Pen، شاشة 6.8 بوصة Dynamic AMOLED، كاميرا 200 ميجابكسل',
                    price=38000,
                    category_id=phones.id,
                    image_url='https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                # Wireless Headphones
                Product(
                    name='AirPods Pro 2nd Generation',
                    description='سماعات AirPods Pro الجيل الثاني مع خاصية إلغاء الضوضاء المحسنة وعمر بطارية أطول',
                    price=1200,
                    category_id=headphones.id,
                    image_url='https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                Product(
                    name='Sony WH-1000XM5',
                    description='سماعات سوني الرائدة مع أفضل تقنية إلغاء ضوضاء في العالم وجودة صوت استثنائية',
                    price=1800,
                    category_id=headphones.id,
                    image_url='https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                # Professional Cameras
                Product(
                    name='Canon EOS R5 - كاميرا احترافية',
                    description='كاميرا كانون R5 الاحترافية مع دقة 45 ميجابكسل وتصوير فيديو 8K RAW، مثالية للمصورين المحترفين',
                    price=125000,
                    category_id=cameras.id,
                    image_url='https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                Product(
                    name='Sony Alpha A7 IV',
                    description='كاميرا سوني Alpha A7 IV مع مستشعر فل فريم 33 ميجابكسل ونظام تركيز تلقائي متطور',
                    price=98000,
                    category_id=cameras.id,
                    image_url='https://images.unsplash.com/photo-1502920917128-1aa500764cbd?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                # Furniture
                Product(
                    name='طقم صالون عصري - 3+2+1',
                    description='طقم صالون عصري فاخر مكون من 3 قطع، تصميم حديث مع خامات عالية الجودة ومفروشات مريحة',
                    price=25000,
                    category_id=furniture.id,
                    image_url='https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                Product(
                    name='طاولة طعام خشبية فاخرة',
                    description='طاولة طعام من الخشب الطبيعي لـ 8 أشخاص، تصميم كلاسيكي أنيق مع كراسي مطابقة',
                    price=15000,
                    category_id=furniture.id,
                    image_url='https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                # Fashion & Accessories
                Product(
                    name='ساعة رولكس سابمارينر - أصلية',
                    description='ساعة رولكس سابمارينر أصلية، موديل حديث مع ضمان الوكالة وحالة ممتازة',
                    price=280000,
                    category_id=fashion.id,
                    image_url='https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                Product(
                    name='حقيبة لويس فيتون - أصلية',
                    description='حقيبة يد لويس فيتون أصلية من مجموعة Neverfull، جلد طبيعي مع رقم سيريال أصلي',
                    price=45000,
                    category_id=fashion.id,
                    image_url='https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                # Jobs
                Product(
                    name='مطور تطبيقات الهاتف المحمول - React Native',
                    description='نبحث عن مطور تطبيقات محمول محترف بخبرة React Native لتطوير تطبيقات متقدمة',
                    price=0,
                    category_id=jobs.id,
                    image_url='https://images.unsplash.com/photo-1550439062-609e1531270e?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                ),
                
                Product(
                    name='مصمم UI/UX محترف',
                    description='فرصة عمل لمصمم واجهات مستخدم ومصمم تجربة مستخدم مبدع للانضمام لفريق التصميم',
                    price=0,
                    category_id=jobs.id,
                    image_url='https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?auto=format&fit=crop&w=800&q=80',
                    user_id=user.id
                )
            ]
            
            for product in products:
                db.session.add(product)
            db.session.commit()

# ===== Routes =====
@app.route('/')
def index():
    featured = Product.query.join(Category).with_entities(
        Product.id, Product.name, Product.description, Product.price, 
        Product.image_url, Product.created_at, Category.name.label('category_name')
    ).order_by(Product.created_at.desc()).limit(8).all()
    return render_template('index.html', featured=featured)

@app.route('/products')
def products():
    category_filter = request.args.get('category')
    
    query = Product.query.join(Category).with_entities(
        Product.id, Product.name, Product.description, Product.price, 
        Product.image_url, Product.created_at, Category.name.label('category_name')
    )
    
    if category_filter:
        query = query.filter(Category.name == category_filter)
    
    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    
    return render_template('products.html', products=products, categories=categories, current_category=category_filter)

@app.route('/products/<int:pid>')
def product_details(pid):
    product = Product.query.join(Category).join(User).with_entities(
        Product.id, Product.name, Product.description, Product.price, 
        Product.image_url, Product.created_at,
        Category.name.label('category_name'),
        User.fullname
    ).filter(Product.id == pid).first()
    
    if not product:
        return redirect(url_for('products'))
    return render_template('product_details.html', product=product)

@app.route('/cars')
def cars():
    cars_category = Category.query.filter_by(name='سيارات مستعملة').first()
    if cars_category:
        cars = Product.query.filter_by(category_id=cars_category.id).all()
    else:
        cars = []
    return render_template('cars.html', cars=cars)

@app.route('/jobs')
def jobs():
    jobs_category = Category.query.filter_by(name='فرص عمل').first()
    jobs = []
    if jobs_category:
        jobs = Product.query.filter_by(category_id=jobs_category.id).all()
    
    # Also search for job-related keywords in all products
    job_keywords = Product.query.filter(
        (Product.name.contains('مطور')) | 
        (Product.name.contains('وظيفة')) |
        (Product.name.contains('عمل'))
    ).all()
    
    # Combine and remove duplicates
    all_jobs = list({job.id: job for job in (jobs + job_keywords)}.values())
    return render_template('jobs.html', jobs=all_jobs)



@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    products_count = Product.query.count()
    users_count = User.query.count()
    
    # Products from last 30 days - simplified for now
    new_products = Product.query.count() # TODO: Add date filtering
    
    admins = User.query.filter_by(role='admin').all()
    
    recent_products = Product.query.join(Category).with_entities(
        Product.id, Product.name, Product.price,
        Category.name.label('category_name')
    ).order_by(Product.created_at.desc()).limit(5).all()

    return render_template('admin_panel.html',
                           products_count=products_count,
                           users_count=users_count,
                           new_products=new_products,
                           admins=admins,
                           recent_products=recent_products)

@app.route('/admin/panel')
def admin_panel():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    products_count = Product.query.count()
    users_count = User.query.count()
    new_products = Product.query.count()
    admins = User.query.filter_by(role='admin').all()
    
    recent_products = Product.query.join(Category).with_entities(
        Product.id, Product.name, Product.price,
        Category.name.label('category_name')
    ).order_by(Product.created_at.desc()).limit(5).all()

    return render_template('admin_panel.html',
                           products_count=products_count,
                           users_count=users_count,
                           new_products=new_products,
                           admins=admins,
                           recent_products=recent_products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['email'] = user.email
            session['fullname'] = user.fullname
            session['role'] = user.role
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='البريد الإلكتروني أو كلمة المرور غير صحيحة')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error='كلمة المرور غير متطابقة')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error='البريد الإلكتروني مستخدم بالفعل')

        hashed_password = generate_password_hash(password)

        new_user = User(
            fullname=fullname,
            email=email,
            phone=phone,
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['email'] = email
        session['fullname'] = fullname
        session['role'] = 'user'

        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category_id'])
        
        # Handle image upload
        image_url = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid conflicts
                import time
                filename = f"{int(time.time())}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_url = f"/static/uploads/{filename}"
        
        new_product = Product(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            image_url=image_url,
            user_id=session['user_id'],
            status='pending'  # Products need admin approval
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        flash('تم إضافة المنتج بنجاح! سيظهر بعد موافقة الإدارة.')
        return redirect(url_for('my_products'))
    
    categories = Category.query.all()
    return render_template('add_product.html', categories=categories)

@app.route('/my_products')
def my_products():
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً')
        return redirect(url_for('login'))
    
    products = Product.query.filter_by(user_id=session['user_id']).join(Category).with_entities(
        Product.id, Product.name, Product.description, Product.price, 
        Product.image_url, Product.status, Product.created_at, Category.name.label('category_name')
    ).order_by(Product.created_at.desc()).all()
    
    return render_template('my_products.html', products=products)

@app.route('/api/my_products/<int:product_id>', methods=['DELETE'])
def delete_my_product(product_id):
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول'}), 401
    
    product = Product.query.filter_by(id=product_id, user_id=session['user_id']).first()
    if not product:
        return jsonify({'error': 'المنتج غير موجود أو ليس لديك صلاحية'}), 404
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف المنتج بنجاح'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# APIs
@app.route('/api/products')
def api_products():
    # Only show approved products to public
    products = Product.query.filter(Product.status == 'approved').join(Category).with_entities(
        Product.id, Product.name, Product.description, Product.price, 
        Product.image_url, Product.created_at, Category.name.label('category_name')
    ).all()
    
    products_list = []
    for p in products:
        products_list.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'image_url': p.image_url,
            'category_name': p.category_name,
            'created_at': p.created_at.isoformat() if p.created_at else None
        })

    return jsonify(products_list)

@app.route('/api/products', methods=['POST'])
def api_add_product():
    if 'user_id' not in session:
        return jsonify({'error': 'يجب تسجيل الدخول'}), 401

    data = request.json or {}
    required = ['name', 'description', 'price', 'category_id']
    if not all(k in data for k in required):
        return jsonify({'error': 'بيانات ناقصة'}), 400

    try:
        new_product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category_id=data['category_id'],
            image_url=data.get('image_url', ''),
            user_id=session['user_id']
        )
        
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'success': True, 'product_id': new_product.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin API Routes
@app.route('/api/admin/products')
def api_admin_products():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    products = Product.query.join(Category).join(User).with_entities(
        Product.id, Product.name, Product.description, Product.price, 
        Product.image_url, Product.status, Product.created_at,
        Category.name.label('category_name'),
        User.fullname.label('seller_name')
    ).all()
    
    products_list = []
    for p in products:
        products_list.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'image_url': p.image_url,
            'status': p.status,
            'category_name': p.category_name,
            'seller_name': p.seller_name,
            'created_at': p.created_at.isoformat() if p.created_at else None
        })

    return jsonify(products_list)

@app.route('/api/admin/products/<int:product_id>', methods=['PUT'])
def api_admin_update_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    product = Product.query.get_or_404(product_id)
    data = request.json or {}
    
    try:
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'image_url' in data:
            product.image_url = data['image_url']
        if 'status' in data:
            product.status = data['status']
            
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
def api_admin_delete_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/products/<int:product_id>/approve', methods=['POST'])
def api_admin_approve_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    product = Product.query.get_or_404(product_id)
    
    try:
        product.status = 'approved'
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم قبول المنتج'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/products/<int:product_id>/reject', methods=['POST'])
def api_admin_reject_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    product = Product.query.get_or_404(product_id)
    
    try:
        product.status = 'rejected'
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم رفض المنتج'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def api_categories():
    categories = Category.query.all()
    categories_list = [{'id': c.id, 'name': c.name} for c in categories]
    return jsonify(categories_list)

@app.route('/api/admin/users')
def api_admin_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'fullname': user.fullname,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    
    return jsonify(users_list)

@app.route('/api/admin/categories', methods=['POST'])
def api_admin_add_category():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    data = request.json or {}
    if 'name' not in data:
        return jsonify({'error': 'اسم الفئة مطلوب'}), 400
    
    # Check if category already exists
    existing = Category.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': 'الفئة موجودة بالفعل'}), 400
    
    try:
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'success': True, 'category_id': new_category.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/categories/<int:category_id>', methods=['PUT'])
def api_admin_update_category(category_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    category = Category.query.get_or_404(category_id)
    data = request.json or {}
    
    if 'name' in data:
        # Check if new name already exists
        existing = Category.query.filter(
            Category.name == data['name'], 
            Category.id != category_id
        ).first()
        if existing:
            return jsonify({'error': 'اسم الفئة موجود بالفعل'}), 400
        
        category.name = data['name']
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/categories/<int:category_id>', methods=['DELETE'])
def api_admin_delete_category(category_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'غير مصرح'}), 403
    
    category = Category.query.get_or_404(category_id)
    
    # Check if category has products
    product_count = Product.query.filter_by(category_id=category_id).count()
    if product_count > 0:
        return jsonify({'error': f'لا يمكن حذف الفئة. يوجد {product_count} منتج في هذه الفئة'}), 400
    
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Healthcheck for uptime monitors
@app.route('/health')
def health():
    return "OK", 200

# Initialize database when module is imported
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
