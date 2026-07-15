#!/usr/bin/env bash
# Database Restore Script for PostgreSQL

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path_to_backup_file.sql.gz>" >&2
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file ${BACKUP_FILE} not found." >&2
    exit 1
fi

echo "=== Starting Database Restore ==="
echo "Restoring from: ${BACKUP_FILE}"

# Run gunzip and psql
# Warning: This will recreate tables and could overwrite newer data.
if gunzip -c "${BACKUP_FILE}" | psql -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "${PGUSER:-postgres}" -d "${PGDATABASE:-ai_product_os}"; then
    echo "Database restoration completed successfully."
else
    echo "ERROR: Database restoration failed." >&2
    exit 1
fi
