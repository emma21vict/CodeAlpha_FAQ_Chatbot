from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

def create_user(name, email, password):
    if User.query.filter_by(email=email).first():
        return None # User exists
        
    hashed_pw = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_pw)
    
    db.session.add(new_user)
    db.session.commit()
    return new_user
