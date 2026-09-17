import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.models import get_admin_by_username

bp = Blueprint("auth", __name__, url_prefix="/admin")


@bp.before_app_request
def load_logged_in_user():
    username = session.get("admin_username")
    g.admin_user = username


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.get("admin_user") is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)

    return wrapped_view


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        error = None
        admin = get_admin_by_username(username)

        if admin is None or not check_password_hash(admin["password_hash"], password):
            error = "Incorrect username or password."

        if error is None:
            session.clear()
            session["admin_username"] = admin["username"]
            next_url = request.form.get("next") or url_for("admin.dashboard")
            return redirect(next_url)

        flash(error)

    return render_template("auth/login.html", next=request.args.get("next", ""))


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for("public.home"))
