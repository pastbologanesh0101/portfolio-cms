import os
import tempfile

from flask import Flask


def create_app(test_config=None, testing=False):
    """Application factory.

    Pass ``testing=True`` (or a ``test_config`` dict with ``TESTING: True``)
    to get an app wired to a throwaway SQLite file that is created and torn
    down for the lifetime of the app instance -- handy for the test suite.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.path.join(app.instance_path, "portfolio.sqlite"),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    if testing or (test_config and test_config.get("TESTING")):
        db_fd, db_path = tempfile.mkstemp(suffix=".sqlite")
        app.config.update(TESTING=True, DATABASE=db_path, WTF_CSRF_ENABLED=False)
        app._test_db_fd = db_fd  # closed by callers that tear the app down

    if test_config:
        app.config.update(test_config)

    from app import db

    db.init_app(app)

    if app.config["TESTING"] or not os.path.exists(app.config["DATABASE"]):
        with app.app_context():
            db.init_db()

    from app import auth

    app.register_blueprint(auth.bp)

    from app import public

    app.register_blueprint(public.bp)

    from app import admin

    app.register_blueprint(admin.bp)

    @app.context_processor
    def inject_globals():
        from flask import g

        return {"logged_in_admin": g.get("admin_user")}

    return app
