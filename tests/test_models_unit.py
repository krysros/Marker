from marker.models import Company, Project, Tag
from marker.models.user import User


def test_user_check_password_failure(dbsession):
    user = User(
        name="pwuser",
        fullname="PW User",
        email="pw@u.com",
        role="user",
        password="correct",
    )
    dbsession.add(user)
    dbsession.flush()
    assert user.check_password("wrong") is False


def test_user_check_password_success(dbsession):
    user = User(
        name="pwuser2",
        fullname="PW 2",
        email="p2@u.com",
        role="user",
        password="correct",
    )
    dbsession.add(user)
    dbsession.flush()
    assert user.check_password("correct") is True


def test_user_check_password_rehash(dbsession):
    """Cover line 51: password rehash when argon2 parameters change."""
    from unittest.mock import MagicMock, patch

    user = User(
        name="pwrehash",
        fullname="Rehash",
        email="rh@u.com",
        role="user",
        password="secret",
    )
    dbsession.add(user)
    dbsession.flush()
    old_hash = user.password
    mock_ph = MagicMock()
    mock_ph.verify.return_value = True
    mock_ph.check_needs_rehash.return_value = True
    mock_ph.hash.side_effect = lambda pw: f"rehashed_{pw}"
    with patch("marker.models.user.ph", mock_ph):
        assert user.check_password("secret") is True
    assert user.password == "rehashed_secret"


def test_user_scalar_count_no_session():
    # User not attached to any session
    user = User(name="orphan", fullname="O", email="o@o.com", role="user", password="x")
    assert user._scalar_count(None) == 0


def test_user_count_properties(dbsession):
    user = User(
        name="cnt_user", fullname="Cnt", email="c@u.com", role="user", password="x"
    )
    dbsession.add(user)
    dbsession.flush()
    assert user.count_companies == 0
    assert user.count_projects == 0
    assert user.count_tags == 0
    assert user.count_contacts == 0
    assert user.count_comments == 0


def test_company_slug():
    c = Company(
        name="Hello World",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    assert c.slug == "hello-world"


def test_company_slug_empty():
    c = Company(
        name=None,
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    assert c.slug == ""


def test_company_scalar_count_no_session():
    c = Company(
        name="Orphan",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    assert c._scalar_count(None) == 0


def test_project_scalar_count_no_session():
    p = Project(
        name="Orphan",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        deadline=None,
        stage=None,
        delivery_method=None,
    )
    assert p._scalar_count(None) == 0


def test_tag_scalar_count_no_session():
    t = Tag(name="Orphan")
    assert t._scalar_count(None) == 0


def test_tag_slug():
    t = Tag(name="My Tag")
    assert t.slug == "my-tag"


def test_project_slug():
    p = Project(
        name="Big Project",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        deadline=None,
        stage=None,
        delivery_method=None,
    )
    assert p.slug == "big-project"
