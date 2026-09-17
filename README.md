# Portfolio CMS

A small, self-contained content management system for a personal portfolio
site, built with Flask and SQLite. It has a public-facing site (homepage,
projects, skills, experience timeline) and a session-authenticated admin
panel for managing all of the content.

## What it does

- **Public site**
  - Homepage: profile (name, tagline, bio, contact email) plus featured
    projects only.
  - `/projects`: the full project list, respecting each project's
    `display_order`.
  - `/skills`: all skills grouped by category.
  - `/experience`: work/experience history sorted reverse-chronologically,
    with a `null` `end_date` correctly rendered and sorted as "present"
    (i.e. it sorts as the most recent entry).
- **Admin panel** (`/admin`, single admin user, session-based login)
  - Edit the singleton profile.
  - Full CRUD for projects, skills, and experience entries.
  - Toggle a project's "featured" status.
  - Drag-and-drop-style reordering of projects, backed by a JSON API
    (`POST /admin/projects/reorder`) that reassigns a clean, contiguous
    `display_order` (`0..n-1`) in one transaction.

## Project layout

```
app/
  __init__.py      # application factory: create_app()
  db.py            # SQLite connection handling + CLI commands
  models.py        # data-access functions (plain sqlite3, no ORM)
  auth.py          # login/logout, login_required decorator
  public.py        # public blueprint (home/projects/skills/experience)
  admin.py         # admin blueprint (CRUD, reorder API, profile editing)
  schema.sql       # table definitions + the singleton profile row
  templates/        # Jinja2 templates (public/, admin/, auth/)
  static/           # plain CSS + a small reorder.js for drag-and-drop
tests/              # pytest suite using Flask's test client
wsgi.py             # entry point: `flask --app wsgi run`
```

## Running it locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Seed the single admin user (reads from env vars, or pass --username/--password)
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=change-me
export FLASK_APP=wsgi.py
flask seed-admin

# Run the dev server
flask run
```

Then visit `http://127.0.0.1:5000/` for the public site, and
`http://127.0.0.1:5000/admin/login` to log in with the credentials you
seeded above.

By default the SQLite database lives at `instance/portfolio.sqlite` and is
created automatically the first time the app starts (via
`flask.instance_path`). To reset it from scratch, run `flask init-db` (this
drops and recreates every table, including the admin user, so re-run
`flask seed-admin` afterward).

### Example: adding your first project

1. Log in at `/admin/login`.
2. From the dashboard, click **New project**, fill in the title,
   description, tech stack, URL, and image alt text, and check **Featured**
   if you want it on the homepage.
3. Back on the dashboard, drag project rows to reorder them — the new order
   is saved automatically via the reorder API.

## Running the tests

```bash
pip install -r requirements.txt
pytest -v
```

The test suite uses `create_app(testing=True)`, which points the app at a
throwaway temporary SQLite file (created and deleted per test) instead of
the real `instance/` database, so tests never touch your local data.

Tests cover: the homepage showing only featured projects, the full project
list respecting `display_order`, experience sorting reverse-chronologically
with `null` `end_date` handled as "present", skills grouped by category,
admin routes requiring login, login success/failure, project create/edit/
delete through the admin panel, the reorder API producing contiguous
positions, and toggling a project's featured flag.

CI runs the same suite on Python 3.11 and 3.12 via
`.github/workflows/tests.yml` on every push and pull request.

## License

MIT — see [LICENSE](LICENSE).
