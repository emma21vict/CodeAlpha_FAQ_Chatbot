from flask import Blueprint, render_template, request, jsonify, session
from utils.decorators import login_required, email_verified_required
from models import Event
from extensions import db

agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/agenda')
@login_required
@email_verified_required
def index():
    return render_template('agenda.html')

@agenda_bp.route('/api/events')
@login_required
def get_events():
    user_id = session.get('user_id')
    events = Event.query.filter_by(user_id=user_id).all()
    event_list = [{"id": e.id, "title": e.title, "start": e.start, "end": e.end} for e in events]
    return jsonify(event_list)

@agenda_bp.route('/api/events', methods=['POST'])
@login_required
def add_event():
    user_id = session.get('user_id')
    data = request.json
    new_event = Event(title=data['title'], start=data['start'], end=data.get('end'), user_id=user_id)
    db.session.add(new_event)
    db.session.commit()
    return jsonify({"id": new_event.id, "message": "Événement ajouté avec succès."})

@agenda_bp.route('/api/events/<int:id>', methods=['DELETE'])
@login_required
def delete_event(id):
    user_id = session.get('user_id')
    event = Event.query.filter_by(id=id, user_id=user_id).first()
    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Événement supprimé."})
    return jsonify({"error": "Non trouvé"}), 404
