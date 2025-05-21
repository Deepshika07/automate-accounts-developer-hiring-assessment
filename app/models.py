from app import db
from datetime import datetime

class ReceiptFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(120), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    is_valid = db.Column(db.Boolean, default=False)
    invalid_reason = db.Column(db.String(255), nullable=True)
    is_processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchased_at = db.Column(db.String(100), nullable=True)
    merchant_name = db.Column(db.String(100), nullable=True)
    total_amount = db.Column(db.String(100), nullable=True)
    file_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
