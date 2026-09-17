DROP TABLE IF EXISTS admin_user;
DROP TABLE IF EXISTS profile;
DROP TABLE IF EXISTS project;
DROP TABLE IF EXISTS skill;
DROP TABLE IF EXISTS experience;

CREATE TABLE admin_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL DEFAULT '',
    tagline TEXT NOT NULL DEFAULT '',
    bio TEXT NOT NULL DEFAULT '',
    contact_email TEXT NOT NULL DEFAULT ''
);

CREATE TABLE project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tech_stack TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    image_alt_text TEXT NOT NULL DEFAULT '',
    display_order INTEGER NOT NULL,
    featured INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE skill (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    proficiency_level TEXT NOT NULL DEFAULT ''
);

CREATE TABLE experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    organization TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    description TEXT NOT NULL DEFAULT ''
);

-- Singleton profile row so the app always has something to edit/render.
INSERT INTO profile (id, name, tagline, bio, contact_email)
VALUES (1, 'Your Name', 'What you do, in a few words', 'Write a short bio here.', 'you@example.com');
