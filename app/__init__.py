from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from app.config import Config
from flask_login import LoginManager
from app.extensions import limiter

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = Config.SECRET_KEY

    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import AdminUser
        if user_id == app.config.get('ADMIN_USERNAME'):
            return AdminUser(user_id)
        return None

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=lambda: generate_csrf())

    from app.routes import main_routes, admin_routes, stats_routes
    app.register_blueprint(main_routes.main_bp)
    app.register_blueprint(admin_routes.admin_bp, url_prefix='/admin')
    app.register_blueprint(stats_routes.stats_bp, url_prefix='/stats')

    return app
