from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.auth import login_required
from app.models import (
    create_experience,
    create_project,
    create_skill,
    delete_experience,
    delete_project,
    delete_skill,
    get_all_experience_reverse_chronological,
    get_all_projects,
    get_all_skills,
    get_experience,
    get_profile,
    get_project,
    get_skill,
    reorder_projects,
    toggle_project_featured,
    update_experience,
    update_profile,
    update_project,
    update_skill,
)

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        projects=get_all_projects(),
        skills=get_all_skills(),
        experience=get_all_experience_reverse_chronological(),
        profile=get_profile(),
    )


# ----------------------------------------------------------------- profile --

@bp.route("/profile", methods=("GET", "POST"))
@login_required
def edit_profile():
    profile = get_profile()
    if request.method == "POST":
        update_profile(
            request.form.get("name", "").strip(),
            request.form.get("tagline", "").strip(),
            request.form.get("bio", "").strip(),
            request.form.get("contact_email", "").strip(),
        )
        flash("Profile updated.")
        return redirect(url_for("admin.edit_profile"))
    return render_template("admin/edit_profile.html", profile=profile)


# ---------------------------------------------------------------- projects --

@bp.route("/projects/new", methods=("GET", "POST"))
@login_required
def new_project():
    if request.method == "POST":
        create_project(
            request.form.get("title", "").strip(),
            request.form.get("description", "").strip(),
            request.form.get("tech_stack", "").strip(),
            request.form.get("url", "").strip(),
            request.form.get("image_alt_text", "").strip(),
            request.form.get("featured") == "on",
        )
        flash("Project created.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/project_form.html", project=None)


@bp.route("/projects/<int:project_id>/edit", methods=("GET", "POST"))
@login_required
def edit_project(project_id):
    project = get_project(project_id)
    if project is None:
        flash("Project not found.")
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        update_project(
            project_id,
            request.form.get("title", "").strip(),
            request.form.get("description", "").strip(),
            request.form.get("tech_stack", "").strip(),
            request.form.get("url", "").strip(),
            request.form.get("image_alt_text", "").strip(),
            request.form.get("featured") == "on",
        )
        flash("Project updated.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/project_form.html", project=project)


@bp.route("/projects/<int:project_id>/delete", methods=("POST",))
@login_required
def remove_project(project_id):
    delete_project(project_id)
    flash("Project deleted.")
    return redirect(url_for("admin.dashboard"))


@bp.route("/projects/<int:project_id>/toggle-featured", methods=("POST",))
@login_required
def toggle_featured(project_id):
    new_value = toggle_project_featured(project_id)
    if new_value is None:
        return jsonify({"error": "not found"}), 404
    if request.accept_mimetypes.best == "application/json" or request.is_json:
        return jsonify({"id": project_id, "featured": bool(new_value)})
    flash("Project updated.")
    return redirect(url_for("admin.dashboard"))


@bp.route("/projects/reorder", methods=("POST",))
@login_required
def reorder():
    """Drag-and-drop-style reorder API: accepts {"order": [id, id, ...]}."""
    data = request.get_json(silent=True) or {}
    ordered_ids = data.get("order", [])
    try:
        ordered_ids = [int(pid) for pid in ordered_ids]
    except (TypeError, ValueError):
        return jsonify({"error": "order must be a list of integer ids"}), 400
    final_order = reorder_projects(ordered_ids)
    return jsonify({"order": final_order})


# ------------------------------------------------------------------ skills --

@bp.route("/skills/new", methods=("GET", "POST"))
@login_required
def new_skill():
    if request.method == "POST":
        create_skill(
            request.form.get("name", "").strip(),
            request.form.get("category", "").strip(),
            request.form.get("proficiency_level", "").strip(),
        )
        flash("Skill created.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/skill_form.html", skill=None)


@bp.route("/skills/<int:skill_id>/edit", methods=("GET", "POST"))
@login_required
def edit_skill(skill_id):
    skill = get_skill(skill_id)
    if skill is None:
        flash("Skill not found.")
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        update_skill(
            skill_id,
            request.form.get("name", "").strip(),
            request.form.get("category", "").strip(),
            request.form.get("proficiency_level", "").strip(),
        )
        flash("Skill updated.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/skill_form.html", skill=skill)


@bp.route("/skills/<int:skill_id>/delete", methods=("POST",))
@login_required
def remove_skill(skill_id):
    delete_skill(skill_id)
    flash("Skill deleted.")
    return redirect(url_for("admin.dashboard"))


# -------------------------------------------------------------- experience --

@bp.route("/experience/new", methods=("GET", "POST"))
@login_required
def new_experience():
    if request.method == "POST":
        create_experience(
            request.form.get("title", "").strip(),
            request.form.get("organization", "").strip(),
            request.form.get("start_date", "").strip(),
            request.form.get("end_date", "").strip() or None,
            request.form.get("description", "").strip(),
        )
        flash("Experience entry created.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/experience_form.html", experience=None)


@bp.route("/experience/<int:experience_id>/edit", methods=("GET", "POST"))
@login_required
def edit_experience(experience_id):
    entry = get_experience(experience_id)
    if entry is None:
        flash("Experience entry not found.")
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        update_experience(
            experience_id,
            request.form.get("title", "").strip(),
            request.form.get("organization", "").strip(),
            request.form.get("start_date", "").strip(),
            request.form.get("end_date", "").strip() or None,
            request.form.get("description", "").strip(),
        )
        flash("Experience entry updated.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/experience_form.html", experience=entry)


@bp.route("/experience/<int:experience_id>/delete", methods=("POST",))
@login_required
def remove_experience(experience_id):
    delete_experience(experience_id)
    flash("Experience entry deleted.")
    return redirect(url_for("admin.dashboard"))
