# Flohmarkt - Arabic Marketplace

## Overview

Flohmarkt is a production-ready Arabic-language marketplace application for buying and selling used products. The platform features comprehensive RTL language support and includes 8 specialized categories with professional Unsplash images. Built with Flask and PostgreSQL, it provides a complete marketplace experience with user authentication, product management, admin approval system, and enhanced professional UI. The platform is fully prepared for deployment on flowmarket.com with SSL/HTTPS support.

## User Preferences

Preferred communication style: Simple, everyday language.
User requests: Professional high-quality images, production deployment on flowmarket.com with full SSL/HTTPS support. Updated currency references from Saudi Riyal to Egyptian Pound and country references from Saudi Arabia to Egypt. Implemented comprehensive SEO optimization including meta tags, Open Graph, Twitter Cards, JSON-LD structured data, robots.txt, dynamic sitemap.xml, and canonical URLs. Upgraded all category "Add Product" buttons to professional medium-sized buttons with (+) icons, attractive green/blue gradient colors, and popup authentication for non-logged users. Production deployment configured for Render with PostgreSQL database, health checks, SSL/HTTPS, and custom domain setup.
Admin credentials: admin@flowmarket.com / admin123 (updated for production)
Test user: user@flowmarket.com / user123

Recent Changes (2025-07-29):
- ✅ COMPLETED: Real-time buyer-seller communication system (2025-07-29 21:10 UTC)
- Full integration with SendGrid for instant email delivery to sellers
- Auto-fill buyer information for registered users (read-only fields)
- Contact seller API working with 5+ test messages successfully saved
- Enhanced email templates with Arabic RTL support and professional formatting
- Messages stored in database for admin tracking and seller reference
- Success messages: "✅ تم إرسال رسالتك إلى البائع بنجاح!" 
- Email notifications sent immediately to seller's registered email address
- No registration required - anonymous buyers can contact sellers directly
- Enhanced UI with visual feedback for readonly fields (gray background)
- ✅ COMPLETED: Auto-approval product management system (2025-07-29 08:55 UTC)
- All products now automatically approved (is_approved = 1) regardless of user type
- Instant product visibility in store/products listings without moderation
- Edit/Delete functionality restricted to admin users only (is_admin = True)
- Enhanced my_products page with admin badges and role-based controls
- Created comprehensive edit_product template with image upload support
- Admin controls clearly distinguished from regular user interface
- Store route compatibility maintained for approved products display
- No pending status or moderation workflow required anymore
- Enhanced permission system for product management operations

Previous Changes (2025-07-28):
- ✅ COMPLETED: Ultra-simplified admin login system (2025-07-28 07:42 UTC)
- Removed "Remember Me" checkbox - automatic session management with Flask-Login
- Simple error message: "خطأ في البريد أو كلمة المرور" for any login errors
- Direct redirect to admin panel after successful login (no flash messages)
- Flask-Login integration replacing manual session management
- Admin credentials admin@flowmarket.com / admin123 working perfectly
- Login redirects admin users directly to /admin_panel without extra messages
- Simplified registration form: only name, email, password (removed phone and confirm password)
- Auto-login after successful registration using Flask-Login
- Updated all route decorators to use Flask-Login's @login_required instead of manual session checks
- Fixed all current_user references in templates and API endpoints
- ✅ COMPLETED: Session management completely modernized with Flask-Login
- API endpoints updated to use current_user.is_authenticated instead of session checks
- All admin API routes properly protected with Flask-Login authentication
- Application running live with simplified login: https://6f60513c-8834-49af-9334-e0fd476a5e81-00-38776ye7bjjmo.picard.replit.dev/

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Custom CSS with RTL support
- **Language Support**: Arabic interface with RTL text direction
- **Responsive Design**: Mobile-friendly layout using CSS Grid and Flexbox
- **Icons**: Font Awesome for UI elements

### Backend Architecture
- **Web Framework**: Flask (Python)
- **Architecture Pattern**: MVC (Model-View-Controller)
- **Session Management**: Flask sessions with secure cookie-based authentication
- **Password Security**: Werkzeug password hashing
- **Database ORM**: Raw SQLite queries with row factory for dictionary-like access

### Data Storage
- **Primary Database**: PostgreSQL with cloud hosting support (PostgreSQL on Render)
- **Database Design**: Relational model with foreign key relationships using SQLAlchemy ORM
- **Connection Management**: SQLAlchemy session management with connection pooling optimized for production
- **Schema**: Users, Categories, and Products tables with proper relationships and automatic admin data initialization
- **Security**: Password hashing with Werkzeug, file upload protection, SSL/HTTPS enforcement

## Key Components

### Authentication System
- **User Registration**: Full name, email, phone, password with confirmation
- **Login System**: Email and password-based authentication
- **Role-Based Access**: User and admin roles with different permissions
- **Session Management**: Server-side session storage with user context

### Product Management
- **Product Listings**: Name, description, price, category, and image URL
- **Categories**: Organized product classification system
- **User-Generated Content**: Users can add their own products
- **Image Handling**: URL-based image storage (external hosting)

### Specialized Sections
- **Used Cars**: Dedicated section for automotive listings
- **Job Opportunities**: Employment listings with optional salary information  
- **Mobile Phones**: Latest smartphones from all major brands
- **Wireless Headphones**: High-quality audio devices
- **Professional Cameras**: DSLR and mirrorless cameras for professionals
- **Furniture**: Modern and classic home furniture
- **Fashion & Accessories**: Designer clothes, watches, and luxury accessories
- **Electronics**: Various electronic devices and tech accessories

### Administrative Features
- **Professional Admin Panel**: Modern dashboard with comprehensive CRUD operations
- **Advanced Product Management**: Create, edit, and delete products with image upload support
- **Category Management**: Full CRUD operations for product categories
- **User Management**: View registered users and administrators with role assignment
- **Statistics Dashboard**: Real-time analytics and platform activity monitoring
- **Role-Based Access Control**: Secure admin-only areas with session management

### Enhanced User Experience
- **Professional Add Product Buttons**: Medium-sized buttons with attractive green/blue gradients and (+) icons
- **Popup Authentication**: Non-logged users see a professional popup requesting login instead of direct redirect
- **Consistent UX**: Unified button design across all category pages and product listings
- **Category-Specific Actions**: Buttons dynamically show appropriate category context in popups

## Data Flow

### User Registration Flow
1. User submits registration form with personal details
2. System validates password confirmation and email uniqueness
3. Password is hashed using Werkzeug security functions
4. User record is created in SQLite database
5. User is redirected to login page

### Product Creation Flow
1. Authenticated user accesses add product form
2. User fills in product details including category selection
3. Form submission triggers database insertion
4. Product is associated with the current user's ID
5. User is redirected to product listing page

### Authentication Flow
1. User submits login credentials
2. System verifies email and password hash
3. Session is established with user ID and role
4. User context is maintained across requests
5. Role-based navigation elements are displayed

## External Dependencies

### Python Packages
- **Flask 3.0.3**: Core web framework
- **Werkzeug 3.0.1**: WSGI utilities and security functions
- **Jinja2 3.1.4**: Template engine for HTML rendering
- **itsdangerous 2.1.2**: Secure data serialization
- **click 8.1.7**: Command-line interface utilities
- **gunicorn 22.0.0**: WSGI HTTP server for production deployment

### Frontend Dependencies
- **Font Awesome 6.5.0**: Icon library via CDN
- **Custom CSS**: Self-contained styling with CSS variables and advanced animations
- **Enhanced JavaScript**: Vanilla JavaScript with popup modal functionality and smooth animations

### External Services
- **Image Hosting**: Products use external image URLs (no local file storage)
- **No Email Service**: Currently no email verification or notifications
- **No Payment Processing**: Platform facilitates connections, not transactions

## Deployment Strategy

### Development Environment
- **Local Development**: Python virtual environment with Flask development server
- **Database**: Local SQLite file (database.db)
- **Configuration**: Environment variables for secrets and database path

### Production Deployment Options
- **Render Platform**: Configured for easy deployment with gunicorn
- **Replit Support**: Ready for online IDE deployment
- **Build Process**: Simple pip install from requirements.txt
- **Health Check**: Endpoint available for uptime monitoring

### Environment Configuration
- **Session Secret**: Configurable via SESSION_SECRET environment variable
- **Database Path**: Configurable via DATABASE_URL environment variable
- **Default Fallbacks**: Secure defaults for development environment

### Scalability Considerations
- **Database**: SQLite suitable for small to medium applications
- **Session Storage**: Server-side sessions may need external store for scaling
- **File Storage**: Image URLs point to external services, no local storage burden
- **Caching**: No current caching layer, could be added for performance optimization