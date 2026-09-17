from app.db import get_db
from tests.conftest import ADMIN_PASSWORD, ADMIN_USERNAME, insert_project


def test_admin_routes_require_login(client):
    response = client.get("/admin/", follow_redirects=False)
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_login_success_redirects_to_dashboard(client, login):
    response = login()
    assert response.status_code == 200
    assert b"Admin dashboard" in response.data


def test_admin_login_failure_shows_error(client, login):
    response = login(password="wrong-password")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Incorrect username or password" in body
    # And the session should not be authenticated.
    dashboard = client.get("/admin/", follow_redirects=False)
    assert dashboard.status_code == 302


def test_create_project_via_admin(app, client, login):
    login()
    response = client.post(
        "/admin/projects/new",
        data={
            "title": "New Project",
            "description": "A cool project",
            "tech_stack": "Flask, SQLite",
            "url": "https://example.com",
            "image_alt_text": "screenshot",
            "featured": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        db = get_db()
        row = db.execute("SELECT * FROM project WHERE title = ?", ("New Project",)).fetchone()
    assert row is not None
    assert row["featured"] == 1


def test_edit_project_via_admin(app, client, login):
    insert_project(app, "Original Title", display_order=0)
    with app.app_context():
        project_id = get_db().execute(
            "SELECT id FROM project WHERE title = ?", ("Original Title",)
        ).fetchone()["id"]

    login()
    response = client.post(
        f"/admin/projects/{project_id}/edit",
        data={
            "title": "Updated Title",
            "description": "Updated description",
            "tech_stack": "",
            "url": "",
            "image_alt_text": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        row = get_db().execute("SELECT * FROM project WHERE id = ?", (project_id,)).fetchone()
    assert row["title"] == "Updated Title"


def test_delete_project_via_admin(app, client, login):
    insert_project(app, "To Delete", display_order=0)
    with app.app_context():
        project_id = get_db().execute(
            "SELECT id FROM project WHERE title = ?", ("To Delete",)
        ).fetchone()["id"]

    login()
    response = client.post(f"/admin/projects/{project_id}/delete", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        row = get_db().execute("SELECT * FROM project WHERE id = ?", (project_id,)).fetchone()
    assert row is None


def test_reorder_projects_updates_positions(app, client, login):
    insert_project(app, "A", display_order=0)
    insert_project(app, "B", display_order=1)
    insert_project(app, "C", display_order=2)

    with app.app_context():
        rows = get_db().execute("SELECT id, title FROM project ORDER BY display_order").fetchall()
    ids_by_title = {row["title"]: row["id"] for row in rows}

    login()
    new_order = [ids_by_title["C"], ids_by_title["A"], ids_by_title["B"]]
    response = client.post(
        "/admin/projects/reorder",
        json={"order": new_order},
    )
    assert response.status_code == 200
    assert response.get_json()["order"] == new_order

    with app.app_context():
        rows = get_db().execute("SELECT id, display_order FROM project ORDER BY display_order").fetchall()
    ordered_ids = [row["id"] for row in rows]
    assert ordered_ids == new_order
    # And positions are contiguous starting at 0.
    assert [row["display_order"] for row in rows] == [0, 1, 2]


def test_toggle_featured_via_admin(app, client, login):
    insert_project(app, "Toggle Me", display_order=0, featured=False)
    with app.app_context():
        project_id = get_db().execute(
            "SELECT id FROM project WHERE title = ?", ("Toggle Me",)
        ).fetchone()["id"]

    login()
    response = client.post(
        f"/admin/projects/{project_id}/toggle-featured",
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    assert response.get_json()["featured"] is True

    with app.app_context():
        row = get_db().execute("SELECT featured FROM project WHERE id = ?", (project_id,)).fetchone()
    assert row["featured"] == 1
