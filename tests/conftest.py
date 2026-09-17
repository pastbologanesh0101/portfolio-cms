import os

import pytest

from app import create_app
from app.db import get_db, seed_admin

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "correct-horse-battery-staple"


@pytest.fixture
def app():
    application = create_app(testing=True)

    with application.app_context():
        seed_admin(ADMIN_USERNAME, ADMIN_PASSWORD)

    yield application

    db_path = application.config["DATABASE"]
    fd = getattr(application, "_test_db_fd", None)
    if fd is not None:
        try:
            os.close(fd)
        except OSError:
            pass
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(client):
    def _login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD):
        return client.post(
            "/admin/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    return _login


def insert_project(app, title, display_order, featured=False, **kwargs):
    with app.app_context():
        db = get_db()
        db.execute(
            """INSERT INTO project
               (title, description, tech_stack, url, image_alt_text, display_order, featured)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                title,
                kwargs.get("description", ""),
                kwargs.get("tech_stack", ""),
                kwargs.get("url", ""),
                kwargs.get("image_alt_text", ""),
                display_order,
                int(featured),
            ),
        )
        db.commit()


def insert_skill(app, name, category, proficiency_level=""):
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO skill (name, category, proficiency_level) VALUES (?, ?, ?)",
            (name, category, proficiency_level),
        )
        db.commit()


def insert_experience(app, title, organization, start_date, end_date=None, description=""):
    with app.app_context():
        db = get_db()
        db.execute(
            """INSERT INTO experience (title, organization, start_date, end_date, description)
               VALUES (?, ?, ?, ?, ?)""",
            (title, organization, start_date, end_date, description),
        )
        db.commit()
