from tests.conftest import insert_experience, insert_project, insert_skill


def test_homepage_shows_only_featured_projects(app, client):
    insert_project(app, "Featured One", display_order=0, featured=True)
    insert_project(app, "Not Featured", display_order=1, featured=False)
    insert_project(app, "Featured Two", display_order=2, featured=True)

    response = client.get("/")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Featured One" in body
    assert "Featured Two" in body
    assert "Not Featured" not in body


def test_full_projects_list_respects_display_order(app, client):
    # Insert out of order to make sure the page sorts by display_order, not id.
    insert_project(app, "Third", display_order=2)
    insert_project(app, "First", display_order=0)
    insert_project(app, "Second", display_order=1)

    response = client.get("/projects")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    first_pos = body.index("First")
    second_pos = body.index("Second")
    third_pos = body.index("Third")
    assert first_pos < second_pos < third_pos


def test_projects_list_includes_non_featured_projects_too(app, client):
    insert_project(app, "Only Project", display_order=0, featured=False)

    response = client.get("/projects")

    assert "Only Project" in response.get_data(as_text=True)


def test_experience_page_sorts_reverse_chronological_with_present_first(app, client):
    insert_experience(app, "Junior Dev", "OldCo", start_date="2018-01", end_date="2019-12")
    insert_experience(app, "Senior Dev", "CurrentCo", start_date="2022-01", end_date=None)
    insert_experience(app, "Mid Dev", "MidCo", start_date="2020-01", end_date="2021-12")

    response = client.get("/experience")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "present" in body

    senior_pos = body.index("Senior Dev")
    mid_pos = body.index("Mid Dev")
    junior_pos = body.index("Junior Dev")
    # The ongoing ("present") role should sort first, most recent to oldest after that.
    assert senior_pos < mid_pos < junior_pos


def test_skills_page_groups_by_category(app, client):
    insert_skill(app, "Python", "Languages", "Advanced")
    insert_skill(app, "JavaScript", "Languages", "Intermediate")
    insert_skill(app, "Flask", "Frameworks", "Advanced")

    response = client.get("/skills")
    body = response.get_data(as_text=True)

    assert response.status_code == 200

    # Slice the body into per-category chunks (by heading) and verify each
    # skill lands under the right category heading, regardless of the order
    # categories happen to be rendered in.
    languages_start = body.index("Languages")
    frameworks_start = body.index("Frameworks")
    if languages_start < frameworks_start:
        languages_chunk = body[languages_start:frameworks_start]
        frameworks_chunk = body[frameworks_start:]
    else:
        frameworks_chunk = body[frameworks_start:languages_start]
        languages_chunk = body[languages_start:]

    assert "Python" in languages_chunk
    assert "JavaScript" in languages_chunk
    assert "Flask" not in languages_chunk

    assert "Flask" in frameworks_chunk
    assert "Python" not in frameworks_chunk
    assert "JavaScript" not in frameworks_chunk
