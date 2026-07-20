from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def email_verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        from models.user import User
        user = User.query.get(session['user_id'])
        if not user or not user.email_verified:
            flash("Veuillez vérifier votre email pour accéder à cette page.", "warning")
            return redirect(url_for('auth.verify_pending'))
        
        return f(*args, **kwargs)
    return decorated_function
