from extensions import db

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Text, nullable=False)
