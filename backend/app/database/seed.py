import logging

from app.core.security import get_password_hash
from app.database.session import SessionLocal
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace

logger = logging.getLogger("app.database.seed")


def seed_db():
    db = SessionLocal()
    try:
        # Check if users already exist
        admin_email = "admin@productos.com"
        admin_user = db.query(User).filter_by(email=admin_email).first()
        if admin_user:
            logger.info("Database already seeded.")
            return

        logger.info("Seeding default database records...")

        # 1. Create Default Admin User
        admin = User(
            email=admin_email,
            username="admin",
            full_name="System Administrator",
            password_hash=get_password_hash("AdminPass123!"),
            timezone="UTC",
            language="en",
            is_verified=True,
            is_active=True,
            preferences={},
        )
        db.add(admin)
        db.flush()

        # 2. Create Default Organization
        org = Organization(
            name="Acme Corp",
            slug="acme-corp",
            owner_id=admin.id,
            plan="enterprise",
            status="active",
        )
        db.add(org)
        db.flush()

        # 3. Create Default Workspaces
        engineering = Workspace(
            organization_id=org.id,
            name="Engineering",
            description="Core engineering workspace.",
            icon="code",
            color="#6366f1",
            visibility="private",
            archived=False,
        )
        product = Workspace(
            organization_id=org.id,
            name="Product Management",
            description="Product design and roadmap workspace.",
            icon="compass",
            color="#ec4899",
            visibility="public",
            archived=False,
        )
        db.add(engineering)
        db.add(product)
        db.flush()

        # 4. Map Admin memberships
        mem1 = Membership(
            user_id=admin.id,
            workspace_id=engineering.id,
            role="Owner",
        )
        mem2 = Membership(
            user_id=admin.id,
            workspace_id=product.id,
            role="Owner",
        )
        db.add(mem1)
        db.add(mem2)

        db.commit()
        logger.info(
            "Successfully seeded database with admin user, Acme Corp organization, and Engineering & Product workspaces."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_db()
