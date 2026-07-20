from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import limiter, db
from services.auth_service import authenticate_user, create_user
import secrets
from datetime import datetime, timedelta
from services.email_service import send_reset_email, send_verification_email
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash(f"Bienvenue, {user.name} !", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Email ou mot de passe incorrect.", "error")
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash("Tous les champs sont requis.", "error")
            return redirect(url_for('auth.register'))
            
        user = create_user(name, email, password)
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash("Inscription réussie ! Bienvenue sur la plateforme.", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Cet email est déjà utilisé.", "error")
            
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/verify-pending')
def verify_pending():
    return render_template('verify_pending.html')

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        flash("Ce lien de vérification est invalide.", "error")
        return redirect(url_for('auth.login'))
        
    if user.email_verification_expires_at < datetime.utcnow():
        flash("Ce lien de vérification a expiré.", "error")
        return redirect(url_for('auth.login'))
        
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires_at = None
    db.session.commit()
    
    flash("Votre email a été vérifié avec succès ! Vous pouvez maintenant accéder à votre compte.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Simulation
        token = secrets.token_urlsafe(32)
        send_reset_email(email, token)
        flash("Si un compte existe avec cet email, un lien de réinitialisation vous a été envoyé.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('forgot.html')
