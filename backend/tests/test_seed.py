from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace


def test_seed_database(db):
    """
    Verify that the seeding script runs without errors and correctly provisions elements.
    """
    # Run seeder using the clean test DB session
    # We patch SessionLocal inside seed_db to yield our test DB session
    import app.database.seed as seed_mod

    original_session_local = seed_mod.SessionLocal
    try:
        # Override SessionLocal to return our test db session
        seed_mod.SessionLocal = lambda: db

        # Run seeder
        seed_mod.seed_db()

        # Run again to verify idempotency
        seed_mod.seed_db()

        # Query and verify
        admin = db.query(User).filter_by(email="admin@productos.com").first()
        assert admin is not None
        assert admin.username == "admin"

        org = db.query(Organization).filter_by(owner_id=admin.id).first()
        assert org is not None
        assert org.name == "Acme Corp"
        assert org.slug == "acme-corp"

        workspaces = db.query(Workspace).filter_by(organization_id=org.id).all()
        assert len(workspaces) == 2
        names = {w.name for w in workspaces}
        assert "Engineering" in names
        assert "Product Management" in names

        memberships = db.query(Membership).filter_by(user_id=admin.id).all()
        assert len(memberships) == 2

    finally:
        seed_mod.SessionLocal = original_session_local
