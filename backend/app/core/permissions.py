from enum import StrEnum


class Permission(StrEnum):
    # Organization Permissions
    ORG_READ = "org:read"
    ORG_WRITE = "org:write"
    ORG_DELETE = "org:delete"

    # Workspace Permissions
    WORKSPACE_READ = "workspace:read"
    WORKSPACE_WRITE = "workspace:write"
    WORKSPACE_DELETE = "workspace:delete"
    WORKSPACE_INVITE = "workspace:invite"

    # Project Permissions
    PROJECT_READ = "project:read"
    PROJECT_WRITE = "project:write"
    PROJECT_DELETE = "project:delete"

    # Document Permissions
    DOCUMENT_READ = "document:read"
    DOCUMENT_WRITE = "document:write"
    DOCUMENT_DELETE = "document:delete"

    # Audit & System Logs
    AUDIT_READ = "audit:read"


class Role(StrEnum):
    OWNER = "Owner"
    ADMIN = "Admin"
    PRODUCT_MANAGER = "Product Manager"
    DEVELOPER = "Developer"
    QA = "QA"
    DESIGNER = "Designer"
    VIEWER = "Viewer"


# Mapping from Roles to Permissions
ROLE_PERMISSIONS = {
    Role.OWNER: set(Permission),
    Role.ADMIN: {
        Permission.ORG_READ,
        Permission.ORG_WRITE,
        Permission.WORKSPACE_READ,
        Permission.WORKSPACE_WRITE,
        Permission.WORKSPACE_INVITE,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.PROJECT_DELETE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
        Permission.DOCUMENT_DELETE,
        Permission.AUDIT_READ,
    },
    Role.PRODUCT_MANAGER: {
        Permission.ORG_READ,
        Permission.WORKSPACE_READ,
        Permission.WORKSPACE_INVITE,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.PROJECT_DELETE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
        Permission.DOCUMENT_DELETE,
    },
    Role.DEVELOPER: {
        Permission.ORG_READ,
        Permission.WORKSPACE_READ,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
    },
    Role.QA: {
        Permission.ORG_READ,
        Permission.WORKSPACE_READ,
        Permission.PROJECT_READ,
        Permission.DOCUMENT_READ,
    },
    Role.DESIGNER: {
        Permission.ORG_READ,
        Permission.WORKSPACE_READ,
        Permission.PROJECT_READ,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
    },
    Role.VIEWER: {
        Permission.ORG_READ,
        Permission.WORKSPACE_READ,
        Permission.PROJECT_READ,
        Permission.DOCUMENT_READ,
    },
}


def role_has_permission(role: str, permission: Permission) -> bool:
    """
    Check if a given role name has the requested permission.
    """
    try:
        role_enum = Role(role)
        permissions = ROLE_PERMISSIONS.get(role_enum, set())
        return permission in permissions
    except ValueError:
        return False
