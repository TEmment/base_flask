
import rq
from flask import Flask, jsonify, make_response, render_template
from flask_caching import Cache
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

# get extensions
db = SQLAlchemy()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
migrate = Migrate()
mail = Mail()
login = LoginManager()


def not_found_error(error):
    # abort response for 404
    return render_template("errors/404.html"), 404


def internal_error(error):
    # abort response for 500
    db.session.rollback()
    return render_template("errors/500.html"), 500


def make_alert_response(msg, status=None):
    if not status:
        status = 200
    return make_response(jsonify({'message': msg}), status)


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    # intilize cache
    cache.init_app(app)

    # initialise extensions
    db.init_app(app)

    @app.context_processor
    def inject_globals():
        code_version = app.config['CODE_VERSION']
        environment = app.config['ENVIRONMENT']

        return dict(code_version=code_version, environment=environment)

    migrate.init_app(app, db)

    mail.init_app(app)
    login.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # REDIS and rq stuff for background jobs
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('tasks', connection=app.redis)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp, url_prefix='/error')

    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)

    from app.core import bp as core_bp
    app.register_blueprint(core_bp, url_prefix='/core')

    return app


# Import Models
from app.models import *  # nopep8 # noqa
