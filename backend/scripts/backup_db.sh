#!/usr/bin/env bash
# Database Backup Script for PostgreSQL
# Restrict execution permissions using: chmod 700 backup_db.sh

set -euo pipefail

# Configurations
BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"
RETENTION_DAYS=7
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/postgres_backup_${TIMESTAMP}.sql.gz"

echo "=== Starting Database Backup ==="
echo "Time: $(date)"
echo "Target File: ${BACKUP_FILE}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Run pg_dump (assumes environment vars PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE are set)
if pg_dump -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "${PGUSER:-postgres}" -d "${PGDATABASE:-ai_product_os}" | gzip > "${BACKUP_FILE}"; then
    echo "Backup completed successfully."
    chmod 600 "${BACKUP_FILE}"
else
    echo "ERROR: Backup failed." >&2
    exit 1
fi

# Retention cleanup
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f -name "postgres_backup_*.sql.gz" -mtime +"${RETENTION_DAYS}" -exec rm -f {} \; -print
echo "Backup execution finished successfully."
