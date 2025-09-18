
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")
app.config['DATABASE'] = os.getenv("DATABASE_URL", "database.db")

# ===== Helpers =====
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category_id INTEGER,
                image_url TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # seed categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            for c in ['سيارات مستعملة', 'إلكترونيات', 'أثاث منزلي', 'ملابس وإكسسوارات']:
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (c,))

        # seed admin
        cursor.execute("SELECT * FROM users WHERE email = 'admin@flohmarkt.com'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (fullname, email, password, role) VALUES (?, ?, ?, ?)",
                ('مدير النظام', 'admin@flohmarkt.com', generate_password_hash('admin123'), 'admin')
            )

        # seed user
        cursor.execute("SELECT * FROM users WHERE email = 'user@example.com'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (fullname, email, phone, password) VALUES (?, ?, ?, ?)",
                ('مستخدم تجريبي', 'user@example.com', '0123456789', generate_password_hash('password123'))
            )

        # seed products
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT id FROM categories WHERE name = 'إلكترونيات'")
            electronics_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM categories WHERE name = 'سيارات مستعملة'")
            cars_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM users WHERE email = 'user@example.com'")
            user_id = cursor.fetchone()[0]
            products = [
                ('ساعة ذكية - Apple Watch Series 5', 'ساعة ذكية بحالة ممتازة، شاشة بحالة ممتازة، جميع الميزات تعمل بشكل ممتاز', 5330, electronics_id, 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=764&q=80', user_id),
                ('مرسيدس بنز C200 موديل 2018', 'سيارة مرسيدس بنز فخمة، حالة ممتازة، فل كامل، صيانة دورية، بدون حوادث، 40,000 كم فقط', 850000, cars_id, 'https://images.unsplash.com/photo-1542362567-b07e54358753?auto=format&fit=crop&w=1170&q=80', user_id),
                ('مطور واجهات أمامية (Frontend Developer)', 'نبحث عن مطور واجهات أمامية مبدع للانضمام لفريقنا، خبرة لا تقل عن 3 سنوات', 0, electronics_id, 'https://images.unsplash.com/photo-1550439062-609e1531270e?auto=format&fit=crop&w=1170&q=80', user_id)
            ]
            for p in products:
                cursor.execute(
                    "INSERT INTO products (name, description, price, category_id, image_url, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                    p
                )

        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ===== Routes =====
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT p.*, c.name AS category_name FROM products p LEFT JOIN categories c ON c.id = p.category_id ORDER BY created_at DESC LIMIT 8")
    featured = cursor.fetchall()
    return render_template('index.html', featured=featured)

@app.route('/products')
def products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT p.*, c.name AS category_name FROM products p LEFT JOIN categories c ON c.id = p.category_id ORDER BY created_at DESC")
    products = cursor.fetchall()
    return render_template('products.html', products=products)

@app.route('/products/<int:pid>')
def product_details(pid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT p.*, c.name AS category_name, u.fullname FROM products p LEFT JOIN categories c ON c.id = p.category_id LEFT JOIN users u ON u.id = p.user_id WHERE p.id = ?", (pid,))
    product = cursor.fetchone()
    if not product:
        return redirect(url_for('products'))
    return render_template('product_details.html', product=product)

@app.route('/cars')
def cars():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT p.*, c.name AS category_name FROM products p WHERE category_id = (SELECT id FROM categories WHERE name = 'سيارات مستعملة')")
    cars = cursor.fetchall()
    return render_template('cars.html', cars=cars)

@app.route('/jobs')
def jobs():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT p.*, c.name AS category_name FROM products p WHERE p.name LIKE '%مطور%' OR p.name LIKE '%وظيفة%'")
    jobs = cursor.fetchall()
    return render_template('jobs.html', jobs=jobs)

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category'])
        image_url = request.form.get('image_url', '')
        user_id = session['user_id']

        cursor.execute(
            "INSERT INTO products (name, description, price, category_id, image_url, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, price, category_id, image_url, user_id)
        )
        db.commit()
        return redirect(url_for('products'))

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    return render_template('add_product.html', categories=categories)

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE created_at >= date('now', '-30 days')")
    new_products = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM users WHERE role = 'admin'")
    admins = cursor.fetchall()

    cursor.execute("SELECT p.*, c.name AS category_name FROM products p LEFT JOIN categories c ON c.id = p.category_id ORDER BY created_at DESC LIMIT 5")
    recent_products = cursor.fetchall()

    return render_template('admin.html',
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

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['fullname'] = user['fullname']
            session['role'] = user['role']
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

        hashed_password = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (fullname, email, phone, password) VALUES (?, ?, ?, ?)",
                (fullname, email, phone, hashed_password)
            )
            db.commit()

            session['user_id'] = cursor.lastrowid
            session['email'] = email
            session['fullname'] = fullname
            session['role'] = 'user'

            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='البريد الإلكتروني مستخدم بالفعل')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# APIs
@app.route('/api/products')
def api_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    products_list = []
    for p in products:
        products_list.append({
            'id': p['id'],
            'name': p['name'],
            'description': p['description'],
            'price': p['price'],
            'image_url': p['image_url'],
            'category_id': p['category_id'],
            'created_at': p['created_at']
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

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (name, description, price, category_id, image_url, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (data['name'], data['description'], data['price'], data['category_id'], data.get('image_url', ''), session['user_id'])
        )
        db.commit()
        return jsonify({'success': True, 'product_id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Healthcheck for uptime monitors
@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
