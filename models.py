from app import db
from datetime import datetime
from flask_login import UserMixin

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationship
    products = db.relationship('Product', backref='category', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True, unique=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    products = db.relationship('Product', backref='user', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    negotiations = db.relationship('PriceNegotiation', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'

class PriceNegotiation(db.Model):
    __tablename__ = 'price_negotiations'
    
    id = db.Column(db.Integer, primary_key=True)
    offered_price = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected', 'countered'
    counter_offer = db.Column(db.Float)
    counter_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='sent_negotiations')
    
    def __repr__(self):
        return f'<PriceNegotiation {self.offered_price} for Product {self.product_id}>'

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_email = db.Column(db.String(120), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)  # Track email delivery status
    email_sent_at = db.Column(db.DateTime, nullable=True)  # When email was sent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields for reply threading
    is_reply = db.Column(db.Boolean, default=False)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)
    
    # Relationships
    product = db.relationship('Product', backref='messages')
    seller = db.relationship('User', backref='received_messages')
    replies = db.relationship('Message', backref=db.backref('parent', remote_side=[id]))
    
    def __repr__(self):
        return f'<Message from {self.buyer_email} to {self.seller.email}>'