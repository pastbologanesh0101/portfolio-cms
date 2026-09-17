from flask import Blueprint, render_template

from app.models import (
    get_all_experience_reverse_chronological,
    get_all_projects,
    get_featured_projects,
    get_profile,
    get_skills_grouped_by_category,
)

bp = Blueprint("public", __name__)


@bp.route("/")
def home():
    profile = get_profile()
    featured_projects = get_featured_projects()
    return render_template("public/home.html", profile=profile, projects=featured_projects)


@bp.route("/projects")
def projects():
    all_projects = get_all_projects()
    return render_template("public/projects.html", projects=all_projects)


@bp.route("/skills")
def skills():
    grouped = get_skills_grouped_by_category()
    return render_template("public/skills.html", grouped_skills=grouped)


@bp.route("/experience")
def experience():
    entries = get_all_experience_reverse_chronological()
    return render_template("public/experience.html", entries=entries)
