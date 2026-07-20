from extensions import db
from datetime import datetime
import secrets

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, default=lambda: secrets.token_urlsafe(16))
    
    # Auth
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Roles & Validation
    role = db.Column(db.String(20), default="user") # 'user', 'admin'
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), nullable=True, unique=True)
    email_verification_expires_at = db.Column(db.DateTime, nullable=True)
    preferred_language = db.Column(db.String(5), default="fr")
    
    # SaaS Plans & Stripe
    plan_id = db.Column(db.String(50), default="free")
    subscription_status = db.Column(db.String(20), default="active")
    stripe_customer_id = db.Column(db.String(100), nullable=True, unique=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True, unique=True)
    
    quota_messages = db.Column(db.Integer, default=100)
    quota_used = db.Column(db.Integer, default=0)
    quota_reset_at = db.Column(db.DateTime, nullable=True)
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relations
    messages = db.relationship('Message', backref='user', lazy=True, cascade="all, delete-orphan")
    contacts = db.relationship('Contact', backref='user', lazy=True, cascade="all, delete-orphan")
    settings = db.relationship('Setting', backref='user', lazy=True, cascade="all, delete-orphan")
    events = db.relationship('Event', backref='user', lazy=True, cascade="all, delete-orphan")
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade="all, delete-orphan")
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.email}>'
