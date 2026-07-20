from models.user import User
from extensions import db
from datetime import datetime

def check_and_increment_quota(user_id):
    """
    Vérifie si l'utilisateur a suffisamment de quota.
    Si oui, l'incrémente et renvoie True.
    Sinon, renvoie False.
    """
    user = User.query.get(user_id)
    if not user:
        return False
        
    # Check if a reset is needed (e.g. monthly)
    # Pour le MVP, on suppose que quota_used et quota_messages sont correctement gérés manuellement ou par webhook
    if user.quota_used >= user.quota_messages:
        return False
        
    # Increment
    user.quota_used += 1
    db.session.commit()
    return True
