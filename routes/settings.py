from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils.decorators import login_required, email_verified_required
from models import Setting, Message, User
from extensions import db
import os

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET'])
@login_required
@email_verified_required
def index():
    return render_template('settings.html')

@settings_bp.route('/instructions', methods=['GET', 'POST'])
@login_required
def instructions():
    user_id = session.get('user_id')
    setting_inst = Setting.query.filter_by(key='instructions', user_id=user_id).first()
    setting_tone = Setting.query.filter_by(key='tone', user_id=user_id).first()
    
    if request.method == 'POST':
        new_inst = request.form.get('instructions')
        new_tone = request.form.get('tone')
        
        if setting_inst:
            setting_inst.value = new_inst
        else:
            db.session.add(Setting(key='instructions', value=new_inst, user_id=user_id))
            
        if setting_tone:
            setting_tone.value = new_tone
        else:
            db.session.add(Setting(key='tone', value=new_tone, user_id=user_id))
            
        db.session.commit()
        flash("Paramètres de l'IA mis à jour avec succès !", "success")
        return redirect(url_for('settings.instructions'))
        
    return render_template('instructions.html', 
                           instructions=setting_inst.value if setting_inst else "", 
                           tone=setting_tone.value if setting_tone else "Professionnel")

@settings_bp.route('/settings/clear_space', methods=['POST'])
@login_required
def clear_space():
    user_id = session.get('user_id')
    Message.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    flash('Historique des messages effacé avec succès.', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/security', methods=['GET', 'POST'])
@login_required
@email_verified_required
def security():
    if request.method == 'POST':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not check_password_hash(user.password_hash, current_password):
            flash('Mot de passe actuel incorrect', 'error')
        elif new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas', 'error')
        else:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Mot de passe mis à jour avec succès', 'success')
            
        return redirect(url_for('settings.security'))
        
    return render_template('security.html')
