from datetime import datetime
from database import db

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    campaign_id = db.Column(db.String(100), nullable=True)  # Link campaign tracking
    recipient = db.Column(db.String(200), nullable=True)    # Link recipient tracking
    clicks = db.relationship('Click', backref='link', lazy=True)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=False)
    recipient = db.Column(db.String(200), nullable=True)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    referrer = db.Column(db.String(500), nullable=True)
    device_type = db.Column(db.String(50), nullable=True)

class EmailOpen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(100), nullable=False)
    campaign_id = db.Column(db.String(100), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    device_type = db.Column(db.String(50), nullable=True)
    open_count = db.Column(db.Integer, default=1)

class EmailCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)