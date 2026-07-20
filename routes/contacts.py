from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, email_verified_required
from models import Contact
from extensions import db

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/contacts')
@login_required
@email_verified_required
def index():
    user_id = session.get('user_id')
    all_contacts = Contact.query.filter_by(user_id=user_id).all()
    return render_template('contacts.html', contacts=all_contacts)

@contacts_bp.route('/contact/add', methods=['POST'])
@login_required
def add_contact():
    name = request.form.get('name')
    phone = request.form.get('phone')
    context = request.form.get('context')
    
    if name and phone:
        new_contact = Contact(name=name, phone=phone, context=context, user_id=session.get('user_id'))
        db.session.add(new_contact)
        db.session.commit()
        flash(f"Contact {name} ajouté avec succès.", "success")
    return redirect(url_for('contacts.index'))

@contacts_bp.route('/contact/edit/<int:id>', methods=['POST'])
@login_required
def edit_contact(id):
    contact = Contact.query.filter_by(id=id, user_id=session.get('user_id')).first_or_404()
    
    contact.name = request.form.get('name', contact.name)
    contact.phone = request.form.get('phone', contact.phone)
    contact.context = request.form.get('context', contact.context)
    db.session.commit()
    flash(f"Contact {contact.name} modifié avec succès.", "success")
    return redirect(url_for('contacts.index'))

@contacts_bp.route('/contact/delete/<int:id>', methods=['POST'])
@login_required
def delete_contact(id):
    contact = Contact.query.filter_by(id=id, user_id=session.get('user_id')).first()
    if contact:
        db.session.delete(contact)
        db.session.commit()
        flash("Contact supprimé.", "success")
    return redirect(url_for('contacts.index'))
