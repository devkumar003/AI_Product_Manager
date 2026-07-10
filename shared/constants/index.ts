export const API_VERSION = 'v1';

export const PROJECT_STATUS = {
  DRAFT: 'draft',
  ACTIVE: 'active',
  ARCHIVED: 'archived',
} as const;

export const USER_ROLES = {
  ADMIN: 'admin',
  MEMBER: 'member',
  VIEWER: 'viewer',
} as const;

export const SYSTEM_LIMITS = {
  MAX_PROJECT_NAME_LENGTH: 100,
  MAX_PROJECT_DESCRIPTION_LENGTH: 1000,
  MAX_DOCUMENT_TITLE_LENGTH: 200,
} as const;
