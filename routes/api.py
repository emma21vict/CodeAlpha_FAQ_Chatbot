from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from models import User, Message, Contact, Setting
from extensions import db
from services.ai_service import generate_ai_response
from utils.quota import check_and_increment_quota

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/webhook/<public_id>', methods=['POST'])
def whatsapp_reply(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return "User not found", 404
        
    # Récupérer le message et limiter drastiquement la taille (anti-abus / réduction des coûts token)
    incoming_msg = request.form.get('Body', '').strip()[:2000]
    sender = request.form.get('From', '')

    # 1. Quota Check
    if not check_and_increment_quota(user.id):
        # Notify user that the business chatbot is currently unavailable due to quota
        reply_text = "Désolé, cet assistant est temporairement indisponible (Quota atteint). Veuillez contacter l'entreprise directement."
        
        # We don't save this to DB to not pollute the message history with quota errors,
        # or we could save it with a special justification.
        resp = MessagingResponse()
        resp.message(reply_text)
        return str(resp)

    # 2. Gather context
    setting_inst = Setting.query.filter_by(key='instructions', user_id=user.id).first()
    setting_tone = Setting.query.filter_by(key='tone', user_id=user.id).first()
    
    user_settings = {
        'instructions': setting_inst.value if setting_inst else '',
        'tone': setting_tone.value if setting_tone else ''
    }
    
    user_contacts = Contact.query.filter_by(user_id=user.id).all()
    
    # Get last 5 messages for context
    message_history = Message.query.filter_by(user_id=user.id, sender=sender).order_by(Message.timestamp.desc()).limit(5).all()
    message_history.reverse() # Oldest first
    
    # 3. Call AI
    reply_text, justification = generate_ai_response(
        incoming_msg, 
        sender, 
        user_settings, 
        user_contacts, 
        message_history
    )

    # Save to user's DB
    new_message = Message(
        user_id=user.id,
        sender=sender,
        content=incoming_msg,
        reply=reply_text,
        justification=justification
    )
    db.session.add(new_message)
    db.session.commit()

    # Respond via Twilio
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)
