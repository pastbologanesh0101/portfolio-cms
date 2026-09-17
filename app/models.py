"""Data-access helpers. Thin wrappers around sqlite3 so views stay simple."""

from app.db import get_db


# ---------------------------------------------------------------- profile --

def get_profile():
    db = get_db()
    row = db.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    return row


def update_profile(name, tagline, bio, contact_email):
    db = get_db()
    db.execute(
        """UPDATE profile SET name = ?, tagline = ?, bio = ?, contact_email = ?
           WHERE id = 1""",
        (name, tagline, bio, contact_email),
    )
    db.commit()


# --------------------------------------------------------------- projects --

def get_all_projects():
    db = get_db()
    return db.execute("SELECT * FROM project ORDER BY display_order ASC").fetchall()


def get_featured_projects():
    db = get_db()
    return db.execute(
        "SELECT * FROM project WHERE featured = 1 ORDER BY display_order ASC"
    ).fetchall()


def get_project(project_id):
    db = get_db()
    return db.execute("SELECT * FROM project WHERE id = ?", (project_id,)).fetchone()


def create_project(title, description, tech_stack, url, image_alt_text, featured):
    db = get_db()
    max_order = db.execute(
        "SELECT COALESCE(MAX(display_order), -1) AS m FROM project"
    ).fetchone()["m"]
    db.execute(
        """INSERT INTO project
           (title, description, tech_stack, url, image_alt_text, display_order, featured)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (title, description, tech_stack, url, image_alt_text, max_order + 1, int(bool(featured))),
    )
    db.commit()
    _resequence_projects()


def update_project(project_id, title, description, tech_stack, url, image_alt_text, featured):
    db = get_db()
    db.execute(
        """UPDATE project SET title = ?, description = ?, tech_stack = ?, url = ?,
           image_alt_text = ?, featured = ? WHERE id = ?""",
        (title, description, tech_stack, url, image_alt_text, int(bool(featured)), project_id),
    )
    db.commit()


def delete_project(project_id):
    db = get_db()
    db.execute("DELETE FROM project WHERE id = ?", (project_id,))
    db.commit()
    _resequence_projects()


def toggle_project_featured(project_id):
    db = get_db()
    row = db.execute("SELECT featured FROM project WHERE id = ?", (project_id,)).fetchone()
    if row is None:
        return None
    new_value = 0 if row["featured"] else 1
    db.execute("UPDATE project SET featured = ? WHERE id = ?", (new_value, project_id))
    db.commit()
    return new_value


def reorder_projects(ordered_ids):
    """Reassign display_order to a clean, contiguous 0..n-1 sequence.

    ``ordered_ids`` is the full list of project ids in the desired order.
    Any project ids that exist but are missing from the list keep their
    relative order and are appended at the end, so the operation never
    silently drops a project.
    """
    db = get_db()
    existing_ids = [row["id"] for row in db.execute("SELECT id FROM project ORDER BY display_order ASC")]
    seen = set()
    final_order = []
    for pid in ordered_ids:
        if pid in existing_ids and pid not in seen:
            final_order.append(pid)
            seen.add(pid)
    for pid in existing_ids:
        if pid not in seen:
            final_order.append(pid)
            seen.add(pid)

    for position, pid in enumerate(final_order):
        db.execute("UPDATE project SET display_order = ? WHERE id = ?", (position, pid))
    db.commit()
    return final_order


def _resequence_projects():
    """Collapse display_order to a contiguous range after insert/delete."""
    db = get_db()
    rows = db.execute("SELECT id FROM project ORDER BY display_order ASC, id ASC").fetchall()
    for position, row in enumerate(rows):
        db.execute("UPDATE project SET display_order = ? WHERE id = ?", (position, row["id"]))
    db.commit()


# ------------------------------------------------------------------ skills --

def get_all_skills():
    db = get_db()
    return db.execute("SELECT * FROM skill ORDER BY category ASC, name ASC").fetchall()


def get_skills_grouped_by_category():
    """Return a dict of {category: [skill rows]} preserving category name order."""
    skills = get_all_skills()
    grouped = {}
    for skill in skills:
        grouped.setdefault(skill["category"], []).append(skill)
    return grouped


def get_skill(skill_id):
    db = get_db()
    return db.execute("SELECT * FROM skill WHERE id = ?", (skill_id,)).fetchone()


def create_skill(name, category, proficiency_level):
    db = get_db()
    db.execute(
        "INSERT INTO skill (name, category, proficiency_level) VALUES (?, ?, ?)",
        (name, category, proficiency_level),
    )
    db.commit()


def update_skill(skill_id, name, category, proficiency_level):
    db = get_db()
    db.execute(
        "UPDATE skill SET name = ?, category = ?, proficiency_level = ? WHERE id = ?",
        (name, category, proficiency_level, skill_id),
    )
    db.commit()


def delete_skill(skill_id):
    db = get_db()
    db.execute("DELETE FROM skill WHERE id = ?", (skill_id,))
    db.commit()


# -------------------------------------------------------------- experience --

def get_all_experience_reverse_chronological():
    """Sort by start_date descending; a null end_date ("present") sorts first."""
    db = get_db()
    rows = db.execute(
        """SELECT * FROM experience
           ORDER BY (end_date IS NOT NULL) ASC, end_date DESC, start_date DESC"""
    ).fetchall()
    return rows


def get_experience(experience_id):
    db = get_db()
    return db.execute("SELECT * FROM experience WHERE id = ?", (experience_id,)).fetchone()


def create_experience(title, organization, start_date, end_date, description):
    db = get_db()
    db.execute(
        """INSERT INTO experience (title, organization, start_date, end_date, description)
           VALUES (?, ?, ?, ?, ?)""",
        (title, organization, start_date, end_date or None, description),
    )
    db.commit()


def update_experience(experience_id, title, organization, start_date, end_date, description):
    db = get_db()
    db.execute(
        """UPDATE experience SET title = ?, organization = ?, start_date = ?,
           end_date = ?, description = ? WHERE id = ?""",
        (title, organization, start_date, end_date or None, description, experience_id),
    )
    db.commit()


def delete_experience(experience_id):
    db = get_db()
    db.execute("DELETE FROM experience WHERE id = ?", (experience_id,))
    db.commit()


# --------------------------------------------------------------- admin_user --

def get_admin_by_username(username):
    db = get_db()
    return db.execute("SELECT * FROM admin_user WHERE username = ?", (username,)).fetchone()
