# Init DB utility: run once to create tables if migrations are not set up
# Usage (Render Shell or local): python init_db.py
import os
from app import app, db  # expects 'db' SQLAlchemy instance in app.py
try:
    with app.app_context():
        db.create_all()
        print("DB tables created successfully.")
except Exception as e:
    print("DB init error:", e)
    raise