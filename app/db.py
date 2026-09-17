import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    """Return a request-scoped SQLite connection, opening one if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Drop and recreate all tables from schema.sql."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    db.commit()


def seed_admin(username, password):
    """Create or update the single admin user with a hashed password."""
    db = get_db()
    password_hash = generate_password_hash(password)
    db.execute("DELETE FROM admin_user")
    db.execute(
        "INSERT INTO admin_user (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    db.commit()


@click.command("init-db")
def init_db_command():
    """Clear existing data and create fresh tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("seed-admin")
@click.option("--username", default=None, help="Admin username (defaults to ADMIN_USERNAME env var).")
@click.option("--password", default=None, help="Admin password (defaults to ADMIN_PASSWORD env var).")
def seed_admin_command(username, password):
    """Seed (or reset) the single admin user's credentials."""
    import os

    username = username or os.environ.get("ADMIN_USERNAME")
    password = password or os.environ.get("ADMIN_PASSWORD")
    if not username or not password:
        raise click.UsageError(
            "Provide --username/--password or set ADMIN_USERNAME/ADMIN_PASSWORD env vars."
        )
    seed_admin(username, password)
    click.echo(f"Admin user '{username}' seeded.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_admin_command)
