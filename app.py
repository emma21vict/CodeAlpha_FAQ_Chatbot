import os
from flask import Flask, redirect, url_for, request, session, g
from extensions import db, limiter, migrate, babel
import secrets

def create_app():
    app = Flask(__name__, template_folder='frontend', static_folder='frontend/static')
    
    # Sécurité: SECRET_KEY
    env_secret = os.environ.get('SECRET_KEY')
    if not env_secret and os.environ.get('FLASK_ENV') == 'production':
        raise ValueError("No SECRET_KEY set for production application")
    app.secret_key = env_secret or secrets.token_hex(32)
    
    # Sécurité: HTTPS
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Configuration PostgreSQL (ou SQLite en fallback)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///assistant_v2.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuration Babel (i18n)
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['fr', 'en']

    # Load models for SQLAlchemy/Alembic
    import models

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    babel.init_app(app)

    def get_locale():
        # Si la langue est dans l'URL ou session (à implémenter)
        if 'lang' in session:
            return session['lang']
        # Si l'utilisateur est connecté, utiliser sa préférence
        if 'user_id' in session:
            from models.user import User
            user = User.query.get(session['user_id'])
            if user and user.preferred_language:
                return user.preferred_language
        return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
    
    babel.init_app(app, locale_selector=get_locale)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.contacts import contacts_bp
    from routes.settings import settings_bp
    from routes.agenda import agenda_bp
    from routes.api import api_bp
    from routes.help import help_bp
    from routes.billing import billing_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(agenda_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(billing_bp)

    @app.before_request
    def csrf_protect():
        if request.method == "POST":
            # Exempt webhooks from CSRF
            if request.path.startswith('/api/'):
                return
            token = session.get('_csrf_token', None)
            if not token or token != request.form.get('csrf_token'):
                return "Jeton CSRF invalide ou manquant.", 403

    def generate_csrf_token():
        if '_csrf_token' not in session:
            import secrets
            session['_csrf_token'] = secrets.token_hex(16)
        return session['_csrf_token']

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf_token)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    with app.app_context():
        pass

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
