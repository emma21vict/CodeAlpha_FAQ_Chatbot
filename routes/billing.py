import os
import stripe
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from utils.decorators import login_required, email_verified_required
from models.user import User
from models.subscription import Subscription
from models.audit_log import AuditLog
from extensions import db
from datetime import datetime

billing_bp = Blueprint('billing', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Prices mapping (in production, these should be from env or db)
PLANS = {
    'free': {'name': 'Free', 'price': 0, 'quota': 100},
    'starter': {'name': 'Starter', 'price': 900, 'stripe_price_id': os.environ.get('STRIPE_PRICE_STARTER', 'price_1'), 'quota': 2000},
    'pro': {'name': 'Pro', 'price': 1900, 'stripe_price_id': os.environ.get('STRIPE_PRICE_PRO', 'price_2'), 'quota': 10000}
}

@billing_bp.route('/billing')
@login_required
@email_verified_required
def index():
    user = User.query.get(session['user_id'])
    return render_template('billing.html', user=user, plans=PLANS)

@billing_bp.route('/billing/checkout/<plan_name>')
@login_required
@email_verified_required
def checkout(plan_name):
    if plan_name not in ['starter', 'pro']:
        flash("Plan invalide", "error")
        return redirect(url_for('billing.index'))
    
    user = User.query.get(session['user_id'])
    plan = PLANS[plan_name]
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=user.email,
            client_reference_id=str(user.id),
            success_url=url_for('billing.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('billing.index', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Erreur de paiement : {str(e)}", "error")
        return redirect(url_for('billing.index'))

@billing_bp.route('/billing/success')
@login_required
def success():
    # We do NOT update the plan here. We wait for the webhook.
    flash("Paiement initié avec succès ! Votre compte sera mis à jour dans quelques instants.", "success")
    return redirect(url_for('billing.index'))

@billing_bp.route('/api/stripe/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        handle_checkout_session(session_obj)

    return jsonify(success=True)

def handle_checkout_session(session_obj):
    user_id = session_obj.get('client_reference_id')
    stripe_customer_id = session_obj.get('customer')
    stripe_subscription_id = session_obj.get('subscription')
    
    if not user_id:
        return
        
    user = User.query.get(int(user_id))
    if user:
        user.stripe_customer_id = stripe_customer_id
        user.stripe_subscription_id = stripe_subscription_id
        user.subscription_status = 'active'
        # To make it robust, we should query Stripe to know exactly which plan they bought.
        # For MVP, we can fetch the subscription details.
        try:
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            price_id = subscription['items']['data'][0]['price']['id']
            
            # Map price back to our internal plan name
            if price_id == PLANS['pro']['stripe_price_id']:
                user.plan_id = 'pro'
                user.quota_messages = PLANS['pro']['quota']
            elif price_id == PLANS['starter']['stripe_price_id']:
                user.plan_id = 'starter'
                user.quota_messages = PLANS['starter']['quota']
                
            # Log the change
            log = AuditLog(user_id=user.id, action=f"Souscription plan {user.plan_id}", ip_address="stripe_webhook")
            
            # Save subscription history
            sub_history = Subscription(
                user_id=user.id,
                plan_id=user.plan_id,
                status='active',
                stripe_subscription_id=stripe_subscription_id
            )
            
            db.session.add(log)
            db.session.add(sub_history)
            db.session.commit()
            
        except Exception as e:
            print(f"Webhook error: {e}")
