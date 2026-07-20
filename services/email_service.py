import os

def send_verification_email(email, token):
    # En production, envoyer un vrai email
    if os.environ.get('FLASK_ENV') != 'production':
        print(f"\n[EMAIL MOCK] Sending VERIFICATION link to {email}")
        print(f"Link: http://localhost:5000/verify-email/{token}\n")
    return True

def send_reset_email(email, token):
    # En production, envoyer un vrai email
    if os.environ.get('FLASK_ENV') != 'production':
        print(f"\n[EMAIL MOCK] Sending reset password link to {email}")
        print(f"Link: http://localhost:5000/reset-password/{token}\n")
    return True
