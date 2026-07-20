from extensions import db
from datetime import datetime

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    plan_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False) # 'active', 'canceled', 'past_due'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    stripe_subscription_id = db.Column(db.String(100), nullable=True, unique=True)
