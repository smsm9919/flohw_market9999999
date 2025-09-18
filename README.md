# Flohmarkt - Arabic Marketplace Platform

🚀 **Now Live in Production:** [https://flowmarket.com](https://flowmarket.com)

A comprehensive online marketplace platform for buying and selling used products in Egypt, featuring Arabic RTL support, professional design, and complete admin management system.

## 🌟 Features

### For Users
- **Professional Product Listings**: Easy-to-use product upload with image support
- **8 Specialized Categories**: Cars, phones, electronics, headphones, cameras, furniture, fashion, and jobs
- **Arabic RTL Interface**: Full Arabic language support with proper text direction
- **Smart Authentication**: Popup login for guests, direct access for logged-in users
- **Advanced Search & Filtering**: Find products quickly by category and keywords
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

### For Administrators
- **Complete Admin Dashboard**: Manage all platform activities from one place
- **Product Approval System**: Review and approve/reject product listings
- **User Management**: View and manage registered users and their roles
- **Category Management**: Full CRUD operations for product categories
- **Real-time Analytics**: Monitor platform activity and user engagement
- **SEO Management**: Built-in SEO optimization with meta tags and sitemaps

### Technical Features
- **Production-Ready**: Deployed on Render with PostgreSQL database
- **SSL/HTTPS Enabled**: Secure connections with automatic certificate management
- **Health Monitoring**: Built-in health checks and monitoring endpoints
- **Performance Optimized**: Gunicorn with connection pooling and caching
- **SEO Optimized**: Complete SEO setup with Open Graph, Twitter Cards, and structured data

## 🚀 Production Deployment

### Live URLs
- **Main Site**: https://flowmarket.com
- **Admin Panel**: https://flowmarket.com/admin
- **Health Check**: https://flowmarket.com/healthz

### Admin Access
- **Email**: admin@flowmarket.com
- **Password**: admin123

### Test User Account
- **Email**: user@flowmarket.com
- **Password**: user123

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite works locally)
- Git

### Quick Start
```bash
# Clone the repository
git clone <your-repo-url>
cd flohmarkt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_production.txt

# Set environment variables
export SECRET_KEY="your-local-secret-key"
export DATABASE_URL="sqlite:///database.db"
export ADMIN_EMAIL="admin@flowmarket.com"
export ADMIN_PASSWORD="admin123"

# Run the application
python app.py
```

The application will be available at http://localhost:5000

### Environment Variables
Create a `.env.local` file for local development:
```env
SECRET_KEY=flohmarkt_local_secret_key_2025
DATABASE_URL=sqlite:///database.db
ADMIN_EMAIL=admin@flowmarket.com
ADMIN_PASSWORD=admin123
MAX_CONTENT_LENGTH=16777216
```

## 📊 Database Management

### Production Database Backup
```bash
# Set your database URL from Render dashboard
export DATABASE_URL="postgresql://username:password@host:port/database"

# Create backup with timestamp
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database
```bash
# Restore from backup file
psql $DATABASE_URL < backup_file.sql
```

### Local Database Reset
```bash
rm database.db  # Delete local SQLite database
python app.py   # Restart app to recreate tables
```

## 🏗️ Architecture

### Backend Stack
- **Flask 3.0.3**: Modern Python web framework
- **SQLAlchemy 2.0**: Advanced ORM with connection pooling
- **PostgreSQL**: Production database (SQLite for local development)
- **Gunicorn**: Production WSGI server with threading support
- **Werkzeug**: Security utilities for password hashing

### Frontend Stack
- **Jinja2 Templates**: Server-side rendering with Arabic RTL support
- **CSS Variables**: Consistent theming and responsive design
- **Font Awesome**: Professional icons and UI elements
- **Vanilla JavaScript**: Lightweight client-side functionality

### Deployment Infrastructure
- **Render Platform**: Cloud hosting with automatic deployments
- **Let's Encrypt SSL**: Automatic HTTPS certificate management
- **CDN Ready**: Optimized static file delivery
- **Health Monitoring**: Built-in application health checks

## 🎯 Key Workflows

### User Product Submission Flow
1. User clicks "إضافة منتج" button on any category
2. Non-logged users see professional popup requesting login
3. Logged users go directly to product submission form
4. Product is submitted with "pending" status
5. Admin reviews and approves/rejects in admin panel
6. Approved products appear in public listings

### Admin Review Process
1. Admin logs into /admin panel
2. Reviews pending products in "إدارة المنتجات"
3. Views product details, images, and user information
4. Approves or rejects with optional feedback
5. Approved products become visible to all users

### SEO & Discovery
1. Automatic sitemap generation at /sitemap.xml
2. Dynamic meta tags for each product and category
3. Open Graph and Twitter Card support
4. JSON-LD structured data for search engines
5. Robots.txt configuration for crawler guidance

## 🔧 Configuration

### Production Environment Variables
Required environment variables for Render deployment:
- `SECRET_KEY`: Auto-generated secure key
- `DATABASE_URL`: PostgreSQL connection string from Render
- `ADMIN_EMAIL`: Administrator email (admin@flowmarket.com)
- `ADMIN_PASSWORD`: Administrator password (admin123)
- `MAX_CONTENT_LENGTH`: File upload limit (16777216 = 16MB)

### DNS Configuration
For custom domain setup (flowmarket.com):
```
Type: CNAME
Name: @
Value: flowmarket.onrender.com

Type: CNAME  
Name: www
Value: flowmarket.onrender.com
```

## 📈 Monitoring & Analytics

### Application Health
- Health check endpoint: `/healthz`
- Database connectivity monitoring
- Application status and version tracking
- Automatic error logging and reporting

### Performance Metrics
- Gunicorn worker monitoring
- Database connection pooling
- Request/response time tracking
- Error rate monitoring

## 🔒 Security Features

### Authentication & Authorization
- Secure password hashing with Werkzeug
- Session-based authentication
- Role-based access control (admin/user)
- CSRF protection on forms

### Production Security
- HTTPS enforcement with HSTS headers
- Secure cookie configuration
- SQL injection prevention with SQLAlchemy
- File upload validation and sanitization

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and test locally
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use Arabic text for user-facing content
- Maintain RTL text direction support
- Comment complex business logic

## 📞 Support

### Getting Help
- Check the deployment guide in `deployment_guide.md`
- Review Render service logs for error details
- Verify environment variables are set correctly
- Test database connectivity with health check endpoint

### Common Issues
1. **Database Connection Error**: Verify DATABASE_URL environment variable
2. **SSL Certificate Pending**: Wait 10-15 minutes after domain configuration
3. **File Upload Errors**: Check MAX_CONTENT_LENGTH setting
4. **Admin Access Issues**: Verify admin credentials in environment variables

---

**Made with ❤️ for the Egyptian marketplace community**

*Supporting local businesses and sustainable commerce through technology*