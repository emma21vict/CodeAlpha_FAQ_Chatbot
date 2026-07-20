from flask import Blueprint, render_template, request, session, json, Response
from utils.decorators import login_required, email_verified_required
from models import Message, Contact
from extensions import db
import os

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
@email_verified_required
def index():
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    
    # Isolation: only messages belonging to this user
    messages_pagination = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)
    
    total_messages = Message.query.filter_by(user_id=user_id).count()
    active_contacts = Contact.query.filter_by(user_id=user_id).count()
    
    return render_template('dashboard.html', 
                           messages=messages_pagination.items, 
                           pagination=messages_pagination,
                           total_messages=total_messages,
                           active_contacts=active_contacts)

@dashboard_bp.route('/analytics')
@login_required
@email_verified_required
def analytics():
    user_id = session.get('user_id')
    messages = Message.query.filter_by(user_id=user_id).all()
    dates = {}
    for m in messages:
        d = m.timestamp.strftime('%Y-%m-%d')
        dates[d] = dates.get(d, 0) + 1
        
    sorted_dates = sorted(dates.keys())
    counts = [dates[d] for d in sorted_dates]
    chart_data = {'labels': sorted_dates, 'data': counts}
    
    return render_template('analytics.html', chart_data=json.dumps(chart_data))

@dashboard_bp.route('/export/messages')
@login_required
def export_messages():
    user_id = session.get('user_id')
    messages = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc()).all()
    
    def generate():
        yield 'ID,Expediteur,Message,Reponse_IA,Justification,Date\n'
        for m in messages:
            content = m.content.replace('"', '""')
            reply = m.reply.replace('"', '""')
            justif = str(m.justification).replace('"', '""') if m.justification else ""
            yield f'"{m.id}","{m.sender}","{content}","{reply}","{justif}","{m.timestamp}"\n'
            
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=historique_bot.csv"})
