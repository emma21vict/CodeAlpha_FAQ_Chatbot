from extensions import db
from datetime import datetime

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=False)
    justification = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
